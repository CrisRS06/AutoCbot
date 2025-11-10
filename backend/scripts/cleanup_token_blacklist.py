#!/usr/bin/env python3
"""
Token Blacklist Cleanup Script

Removes expired tokens from the blacklist table to prevent table bloat.
Should be run periodically (e.g., daily via cron job).

Usage:
    python scripts/cleanup_token_blacklist.py [--dry-run]

Options:
    --dry-run    Show what would be deleted without actually deleting
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import TokenBlacklist
from utils.config import settings
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_expired_tokens(dry_run=False):
    """
    Remove expired tokens from the blacklist

    Args:
        dry_run: If True, only count tokens without deleting

    Returns:
        Number of tokens removed (or that would be removed in dry-run)
    """
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        # Get current time
        now = datetime.utcnow()

        # Query for expired tokens
        expired_tokens = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < now
        )

        # Count expired tokens
        count = expired_tokens.count()

        if count == 0:
            logger.info("No expired tokens found in blacklist")
            return 0

        if dry_run:
            logger.info(f"[DRY RUN] Would delete {count} expired tokens")

            # Show sample of tokens that would be deleted
            sample = expired_tokens.limit(5).all()
            logger.info("Sample of tokens to be deleted:")
            for token in sample:
                logger.info(
                    f"  - JTI: {token.token_jti[:8]}... "
                    f"| User ID: {token.user_id} "
                    f"| Expired: {token.expires_at} "
                    f"| Type: {token.token_type}"
                )
        else:
            # Delete expired tokens
            expired_tokens.delete(synchronize_session=False)
            db.commit()
            logger.info(f"✅ Successfully deleted {count} expired tokens from blacklist")

        return count

    except Exception as e:
        logger.error(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_blacklist_stats():
    """Get statistics about the token blacklist"""
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    try:
        now = datetime.utcnow()

        total_count = db.query(TokenBlacklist).count()
        expired_count = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < now
        ).count()
        active_count = total_count - expired_count

        logger.info("Token Blacklist Statistics:")
        logger.info(f"  Total tokens: {total_count}")
        logger.info(f"  Active (not expired): {active_count}")
        logger.info(f"  Expired: {expired_count}")

        if total_count > 0:
            logger.info(f"  Expired percentage: {(expired_count/total_count)*100:.1f}%")

        return {
            "total": total_count,
            "active": active_count,
            "expired": expired_count
        }

    finally:
        db.close()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Clean up expired tokens from blacklist"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--stats-only",
        action="store_true",
        help="Only show statistics without cleaning up"
    )

    args = parser.parse_args()

    logger.info("🧹 Starting token blacklist cleanup...")

    # Show statistics
    stats = get_blacklist_stats()

    if args.stats_only:
        logger.info("Stats-only mode, skipping cleanup")
        return 0

    # Perform cleanup
    if stats["expired"] > 0:
        deleted_count = cleanup_expired_tokens(dry_run=args.dry_run)

        if not args.dry_run:
            logger.info(f"Cleanup complete. Removed {deleted_count} expired tokens.")

        return deleted_count
    else:
        logger.info("No cleanup needed")
        return 0


if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result >= 0 else 1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

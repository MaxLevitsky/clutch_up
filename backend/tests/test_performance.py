# Test Case: TC-NFR-012-01
# Requirement: NFR-12
# Feature: F004
# Scenario: Performance - Tournament Creation
# Performance Test: Tournament creation must complete in < 3s (95th percentile)

import pytest
import time
from app.services.tournament_service import TournamentService
from app.repositories.tournament_repository import TournamentRepository
from app.repositories.player_repository import PlayerRepository
from app.database import SessionLocal
from datetime import datetime, timedelta
import statistics


@pytest.fixture
def perf_db():
    """Performance test database fixture"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def perf_tournament_service(perf_db):
    """Performance test tournament service fixture"""
    tournament_repo = TournamentRepository(perf_db)
    player_repo = PlayerRepository(perf_db)
    return TournamentService(tournament_repo, player_repo)


class TestTournamentCreationPerformance:
    """
    NFR-12: Tournament creation must complete in < 3s at 95th percentile
    Test validates that tournament creation operations meet performance SLA
    """

    def test_tournament_creation_performance_single(self, perf_tournament_service):
        """
        Test Case: TC-NFR-012-01 (Single Operation)
        Verify single tournament creation completes in < 3s
        """
        start_time = time.time()

        # Create tournament
        result = perf_tournament_service.create_tournament(
            name="Performance Test Tournament",
            rank_tier="BEGINNER",
            region="NA",
            capacity=32,
            format="Single Elimination",
            start_time=datetime.now() + timedelta(days=30),
            is_team_tournament=False,
            team_size=None
        )

        end_time = time.time()
        duration = end_time - start_time

        # Assert success
        assert result["status"] == "success"

        # NFR-12: Assert duration < 3s
        assert duration < 3.0, f"Tournament creation took {duration:.3f}s, exceeds 3s SLA"

        # Log performance metric
        print(f"\n[OK] Single tournament creation: {duration:.3f}s")

    def test_tournament_creation_performance_95th_percentile(self, perf_tournament_service):
        """
        Test Case: TC-NFR-012-01 (95th Percentile)
        Verify 95th percentile of tournament creations complete in < 3s
        """
        iterations = 20  # Run 20 iterations to calculate 95th percentile
        durations = []

        for i in range(iterations):
            start_time = time.time()

            # Create tournament with unique name
            result = perf_tournament_service.create_tournament(
                name=f"Perf Test {i}",
                rank_tier="BEGINNER",
                region="NA",
                capacity=16,
                format="Single Elimination",
                start_time=datetime.now() + timedelta(days=30),
                is_team_tournament=False,
                team_size=None
            )

            end_time = time.time()
            duration = end_time - start_time
            durations.append(duration)

            # Assert success
            assert result["status"] == "success"

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        median_duration = statistics.median(durations)
        p95_duration = statistics.quantiles(durations, n=20)[18]  # 95th percentile
        max_duration = max(durations)

        # Log performance metrics
        print(f"\n[STATS] Tournament Creation Performance ({iterations} iterations):")
        print(f"   Mean:   {mean_duration:.3f}s")
        print(f"   Median: {median_duration:.3f}s")
        print(f"   95th %: {p95_duration:.3f}s")
        print(f"   Max:    {max_duration:.3f}s")

        # NFR-12: Assert 95th percentile < 3s
        assert p95_duration < 3.0, \
            f"95th percentile ({p95_duration:.3f}s) exceeds 3s SLA"

    def test_tournament_creation_performance_team_tournament(self, perf_tournament_service):
        """
        Test Case: TC-NFR-012-01 (Team Tournament Variant)
        Verify team tournament creation also meets performance SLA
        """
        start_time = time.time()

        # Create team tournament
        result = perf_tournament_service.create_tournament(
            name="Team Perf Test",
            rank_tier="INTERMEDIATE",
            region="EU",
            capacity=16,
            format="Double Elimination",
            start_time=datetime.now() + timedelta(days=30),
            is_team_tournament=True,
            team_size=5
        )

        end_time = time.time()
        duration = end_time - start_time

        # Assert success
        assert result["status"] == "success"

        # NFR-12: Assert duration < 3s
        assert duration < 3.0, \
            f"Team tournament creation took {duration:.3f}s, exceeds 3s SLA"

        # Log performance metric
        print(f"\n[OK] Team tournament creation: {duration:.3f}s")

    def test_tournament_creation_sequential_load(self, perf_tournament_service):
        """
        Test Case: TC-NFR-012-01 (Sequential Load)
        Verify tournament creation performance under sequential load
        Note: For true concurrent load testing, use Locust or JMeter with separate DB connections
        """
        num_iterations = 10
        durations = []

        for i in range(num_iterations):
            start_time = time.time()
            result = perf_tournament_service.create_tournament(
                name=f"Load Test {i}",
                rank_tier="BEGINNER",
                region="NA",
                capacity=16,
                format="Single Elimination",
                start_time=datetime.now() + timedelta(days=30),
                is_team_tournament=False,
                team_size=None
            )
            end_time = time.time()

            durations.append(end_time - start_time)
            assert result["status"] == "success"

        # Calculate statistics
        mean_duration = statistics.mean(durations)
        max_duration = max(durations)

        # Log results
        print(f"\n[STATS] Sequential Load ({num_iterations} iterations):")
        print(f"   Mean:      {mean_duration:.3f}s")
        print(f"   Max:       {max_duration:.3f}s")

        # NFR-12: Assert max duration < 3s
        assert max_duration < 3.0, \
            f"Max duration ({max_duration:.3f}s) exceeds 3s SLA"

    def test_tournament_validation_performance(self, perf_tournament_service):
        """
        Test Case: TC-NFR-012-01 (Validation Performance)
        Verify validation failures also complete quickly
        """
        start_time = time.time()

        # Attempt to create tournament with invalid data
        result = perf_tournament_service.create_tournament(
            name="Invalid Capacity",
            rank_tier="BEGINNER",
            region="NA",
            capacity=0,  # Invalid: below minimum of 1
            format="Single Elimination",
            start_time=datetime.now() + timedelta(days=30),
            is_team_tournament=False,
            team_size=None
        )

        end_time = time.time()
        duration = end_time - start_time

        # Assert validation failed (as expected)
        assert result["status"] == "error"

        # Assert validation completes quickly (< 1s for failures)
        assert duration < 1.0, \
            f"Validation took {duration:.3f}s, should be < 1s"

        print(f"\n[OK] Validation (failure case): {duration:.3f}s")

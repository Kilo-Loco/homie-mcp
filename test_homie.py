"""Tests for Homie MCP companion system."""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from server import (
    EYES,
    HATS,
    RARITIES,
    RARITY_WEIGHTS,
    SPECIES,
    SPRITES,
    STAT_NAMES,
    _get_full_companion,
    _load_state,
    _roll_rarity,
    _roll_stats,
    _save_state,
    _seed_from_name,
    generate_companion,
    render_sprite,
    render_stat_card,
    _get_reaction,
    PET_REACTIONS,
    STATE_FILE,
)
import random


# ---------------------------------------------------------------------------
# Determinism Tests
# ---------------------------------------------------------------------------


class TestDeterminism:
    """Companion generation must be deterministic for the same seed."""

    def test_same_seed_same_companion(self):
        c1 = generate_companion("test-user")
        c2 = generate_companion("test-user")
        assert c1 == c2

    def test_different_seed_different_companion(self):
        c1 = generate_companion("user-a")
        c2 = generate_companion("user-b")
        # Extremely unlikely to be identical
        assert c1 != c2

    def test_seed_is_stable_across_calls(self):
        s1 = _seed_from_name("hello")
        s2 = _seed_from_name("hello")
        assert s1 == s2

    def test_seed_differs_for_different_inputs(self):
        s1 = _seed_from_name("hello")
        s2 = _seed_from_name("world")
        assert s1 != s2

    def test_empty_seed_works(self):
        c = generate_companion("")
        assert c["species"] in SPECIES

    def test_unicode_seed_works(self):
        c = generate_companion("日本語テスト🎮")
        assert c["species"] in SPECIES

    def test_long_seed_works(self):
        c = generate_companion("a" * 10000)
        assert c["species"] in SPECIES


# ---------------------------------------------------------------------------
# Companion Generation Tests
# ---------------------------------------------------------------------------


class TestCompanionGeneration:
    def test_species_is_valid(self):
        for i in range(50):
            c = generate_companion(f"test-{i}")
            assert c["species"] in SPECIES

    def test_rarity_is_valid(self):
        for i in range(50):
            c = generate_companion(f"test-{i}")
            assert c["rarity"] in RARITIES

    def test_eye_is_valid(self):
        for i in range(50):
            c = generate_companion(f"test-{i}")
            assert c["eye"] in EYES

    def test_hat_is_valid(self):
        for i in range(50):
            c = generate_companion(f"test-{i}")
            assert c["hat"] in HATS or c["hat"] == "none"

    def test_common_has_no_hat(self):
        """Common rarity companions should not have hats."""
        for i in range(200):
            c = generate_companion(f"hat-test-{i}")
            if c["rarity"] == "common":
                assert c["hat"] == "none"

    def test_shiny_is_boolean(self):
        c = generate_companion("test")
        assert isinstance(c["shiny"], bool)

    def test_stats_are_present(self):
        c = generate_companion("test")
        for stat in STAT_NAMES:
            assert stat in c["stats"]

    def test_stats_in_valid_range(self):
        for i in range(100):
            c = generate_companion(f"range-{i}")
            for stat in STAT_NAMES:
                assert 1 <= c["stats"][stat] <= 100

    def test_personality_is_set(self):
        c = generate_companion("test")
        assert len(c["personality"]) > 0

    def test_seed_is_preserved(self):
        c = generate_companion("my-seed")
        assert c["seed"] == "my-seed"

    def test_all_species_can_be_generated(self):
        """Over enough seeds, we should see all species appear."""
        seen = set()
        for i in range(1000):
            c = generate_companion(f"species-hunt-{i}")
            seen.add(c["species"])
        # Should hit at least most species with 1000 tries
        assert len(seen) >= len(SPECIES) * 0.7


# ---------------------------------------------------------------------------
# Rarity Distribution Tests
# ---------------------------------------------------------------------------


class TestRarityDistribution:
    def test_rarity_weights_sum_to_100(self):
        assert sum(RARITY_WEIGHTS.values()) == 100

    def test_roll_rarity_returns_valid(self):
        rng = random.Random(42)
        for _ in range(100):
            r = _roll_rarity(rng)
            assert r in RARITIES

    def test_common_is_most_frequent(self):
        """Common should appear most often."""
        counts = {r: 0 for r in RARITIES}
        for i in range(1000):
            c = generate_companion(f"rarity-{i}")
            counts[c["rarity"]] += 1
        assert counts["common"] > counts["uncommon"]
        assert counts["uncommon"] > counts["rare"]

    def test_legendary_is_rarest(self):
        counts = {r: 0 for r in RARITIES}
        for i in range(1000):
            c = generate_companion(f"legend-{i}")
            counts[c["rarity"]] += 1
        assert counts["legendary"] <= counts["epic"]


# ---------------------------------------------------------------------------
# Stats Tests
# ---------------------------------------------------------------------------


class TestStats:
    def test_roll_stats_has_all_names(self):
        rng = random.Random(42)
        stats = _roll_stats(rng, "common")
        for name in STAT_NAMES:
            assert name in stats

    def test_stats_respect_rarity_floor(self):
        """Higher rarity should generally have higher stat floors."""
        from server import STAT_FLOOR

        for rarity in RARITIES:
            rng = random.Random(42)
            stats = _roll_stats(rng, rarity)
            floor = STAT_FLOOR[rarity]
            # At least the peak stat should be above floor
            assert max(stats.values()) >= floor

    def test_stats_have_peak_and_dump(self):
        """Stats should have variety, not all the same value."""
        rng = random.Random(42)
        stats = _roll_stats(rng, "rare")
        values = list(stats.values())
        assert max(values) != min(values)


# ---------------------------------------------------------------------------
# Sprite Rendering Tests
# ---------------------------------------------------------------------------


class TestSpriteRendering:
    def test_all_species_have_sprites(self):
        for species in SPECIES:
            assert species in SPRITES

    def test_all_sprites_have_5_lines(self):
        for species, lines in SPRITES.items():
            assert len(lines) == 5, f"{species} has {len(lines)} lines, expected 5"

    def test_sprite_renders_without_error(self):
        c = generate_companion("render-test")
        sprite = render_sprite(c)
        assert isinstance(sprite, str)
        assert len(sprite) > 0

    def test_eyes_are_substituted(self):
        c = generate_companion("eye-test")
        sprite = render_sprite(c)
        assert "{E}" not in sprite

    def test_shiny_adds_sparkle_border(self):
        c = generate_companion("shiny-test")
        c["shiny"] = True
        sprite = render_sprite(c)
        assert "✨" in sprite

    def test_non_shiny_no_sparkle_border(self):
        c = generate_companion("no-shiny")
        c["shiny"] = False
        sprite = render_sprite(c)
        lines = sprite.split("\n")
        # First and last lines should not be sparkle borders
        assert "✨ ✨ ✨" not in lines[0]

    def test_hat_applied_when_not_none(self):
        c = generate_companion("hat-render")
        c["hat"] = "crown"
        sprite = render_sprite(c)
        assert "♛" in sprite

    def test_no_hat_when_none(self):
        c = generate_companion("no-hat-render")
        c["hat"] = "none"
        sprite = render_sprite(c)
        # Should not have any hat characters
        assert "♛" not in sprite
        assert "[__]" not in sprite


# ---------------------------------------------------------------------------
# Stat Card Rendering Tests
# ---------------------------------------------------------------------------


class TestStatCard:
    def test_renders_without_error(self):
        c = generate_companion("card-test")
        c["name"] = "TestHomie"
        card = render_stat_card(c)
        assert isinstance(card, str)

    def test_contains_name(self):
        c = generate_companion("card-test")
        c["name"] = "Sparkles"
        card = render_stat_card(c)
        assert "Sparkles" in card

    def test_contains_all_stats(self):
        c = generate_companion("card-test")
        c["name"] = "Tester"
        card = render_stat_card(c)
        for stat in STAT_NAMES:
            assert stat in card

    def test_contains_species(self):
        c = generate_companion("card-test")
        c["name"] = "Tester"
        card = render_stat_card(c)
        assert c["species"].upper() in card

    def test_contains_rarity_stars(self):
        c = generate_companion("card-test")
        c["name"] = "Tester"
        card = render_stat_card(c)
        assert "★" in card

    def test_stat_bars_present(self):
        c = generate_companion("card-test")
        c["name"] = "Tester"
        card = render_stat_card(c)
        assert "█" in card or "░" in card


# ---------------------------------------------------------------------------
# State Persistence Tests
# ---------------------------------------------------------------------------


class TestStatePersistence:
    def setup_method(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.tmp_file = Path(self.tmp_dir) / "companion.json"

    def teardown_method(self):
        if self.tmp_file.exists():
            self.tmp_file.unlink()
        os.rmdir(self.tmp_dir)

    @patch("server.STATE_FILE")
    @patch("server.STATE_DIR")
    def test_save_and_load(self, mock_dir, mock_file):
        mock_dir.__truediv__ = lambda s, x: Path(self.tmp_dir) / x
        mock_file.__class__ = type(self.tmp_file)

        with patch("server.STATE_FILE", self.tmp_file), \
             patch("server.STATE_DIR", Path(self.tmp_dir)):
            state = {"seed": "test", "name": "Homie", "hatched_at": 12345, "interactions": 3}
            _save_state(state)
            loaded = _load_state()
            assert loaded == state

    @patch("server.STATE_FILE")
    def test_load_missing_file(self, mock_file):
        mock_file.exists.return_value = False
        result = _load_state()
        assert result is None


# ---------------------------------------------------------------------------
# Reaction Tests
# ---------------------------------------------------------------------------


class TestReactions:
    def test_all_species_have_pet_reactions(self):
        for species in SPECIES:
            assert species in PET_REACTIONS
            assert len(PET_REACTIONS[species]) > 0

    def test_bug_context_reaction(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "debugging a nasty bug")
        assert len(reaction) > 0
        assert c["species"] in reaction

    def test_deploy_context_reaction(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "deploying to production")
        assert len(reaction) > 0
        assert "🚀" in reaction

    def test_test_context_reaction(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "writing unit tests")
        assert len(reaction) > 0

    def test_refactor_context_reaction(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "refactoring the codebase")
        assert "✨" in reaction

    def test_tired_context_reaction(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "so tired need coffee")
        assert len(reaction) > 0

    def test_generic_context_fallback(self):
        c = generate_companion("react-test")
        reaction = _get_reaction(c, "doing some random stuff")
        assert len(reaction) > 0

    def test_high_chaos_bug_reaction(self):
        c = generate_companion("chaos-test")
        c["stats"]["CHAOS"] = 90
        reaction = _get_reaction(c, "everything is broken")
        assert "fine" in reaction.lower() or "chaos" in reaction.lower() or "🔥" in reaction

    def test_high_snark_test_reaction(self):
        c = generate_companion("snark-test")
        c["stats"]["SNARK"] = 90
        c["stats"]["CHAOS"] = 0
        c["stats"]["WISDOM"] = 0
        reaction = _get_reaction(c, "writing tests")
        assert "economy" in reaction.lower() or len(reaction) > 0


# ---------------------------------------------------------------------------
# Edge Cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    def test_all_18_species_exist(self):
        assert len(SPECIES) == 18

    def test_all_5_rarities_exist(self):
        assert len(RARITIES) == 5

    def test_all_6_eyes_exist(self):
        assert len(EYES) == 6

    def test_all_8_hats_exist(self):
        assert len(HATS) == 8

    def test_all_5_stats_exist(self):
        assert len(STAT_NAMES) == 5

    def test_sprite_eye_placeholder_format(self):
        """All sprites should use {E} for eye placeholder."""
        for species, lines in SPRITES.items():
            has_eyes = any("{E}" in line for line in lines)
            assert has_eyes, f"{species} sprite missing {{E}} eye placeholder"

    def test_generate_1000_companions_no_crash(self):
        """Stress test: generate many companions without error."""
        for i in range(1000):
            c = generate_companion(f"stress-{i}")
            render_sprite(c)
            c["name"] = f"Homie-{i}"
            render_stat_card(c)

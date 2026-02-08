#!/usr/bin/env python3
"""
Kill Switch Test Suite
Quick verification that all functionality works correctly.
"""

import os
import sys
import time
from pathlib import Path
from kill_switch import KillSwitch, Level


def test_initialization():
    """Test 1: Initialization"""
    print("\n" + "="*60)
    print("TEST 1: Initialization")
    print("="*60)
    
    ks = KillSwitch(workspace=".")
    status = ks.get_status()
    
    assert status["armed"] == False, "Should start disarmed"
    assert status["triggered"] == False, "Should start not triggered"
    
    print("✅ Initialization successful")
    print(f"   - Armed: {status['armed']}")
    print(f"   - Triggered: {status['triggered']}")
    return ks


def test_arm_disarm(ks):
    """Test 2: Arm/Disarm"""
    print("\n" + "="*60)
    print("TEST 2: Arm/Disarm")
    print("="*60)
    
    # Arm
    assert ks.arm(True), "Should arm successfully"
    status = ks.get_status()
    assert status["armed"] == True, "Should be armed"
    print("✅ Armed successfully")
    
    # Disarm
    assert ks.arm(False), "Should disarm successfully"
    status = ks.get_status()
    assert status["armed"] == False, "Should be disarmed"
    print("✅ Disarmed successfully")


def test_manual_trigger(ks):
    """Test 3: Manual Trigger"""
    print("\n" + "="*60)
    print("TEST 3: Manual Trigger")
    print("="*60)
    
    # Trigger at level 3
    assert ks.trigger(
        reason="Test manual trigger",
        level=Level.CLOSE_ALL,
        triggered_by="test_suite"
    ), "Should trigger successfully"
    
    status = ks.get_status()
    assert status["triggered"] == True, "Should be triggered"
    assert status["trigger_level"] == 3, "Should be level 3"
    assert "Test manual trigger" in status["trigger_reason"], "Reason should be recorded"
    
    print("✅ Manual trigger successful")
    print(f"   - Level: {status['trigger_level']} ({status['trigger_level_name']})")
    print(f"   - Reason: {status['trigger_reason']}")
    print(f"   - Triggered by: {status['triggered_by']}")
    
    # Try to trigger again (should fail)
    assert not ks.trigger("Second trigger", level=4), "Should not trigger twice"
    print("✅ Cannot trigger twice (as expected)")


def test_cooldown(ks):
    """Test 4: Cooldown Period"""
    print("\n" + "="*60)
    print("TEST 4: Cooldown Period")
    print("="*60)
    
    status = ks.get_status()
    assert status["cooldown_remaining_hours"] > 0, "Should be in cooldown"
    print(f"✅ Cooldown active: {status['cooldown_remaining_hours']:.1f}h remaining")
    
    # Try to reset (should fail - in cooldown)
    assert not ks.reset(authorized_by="test_suite"), "Should not reset during cooldown"
    print("✅ Cannot reset during cooldown (as expected)")


def test_force_reset(ks):
    """Test 5: Force Reset"""
    print("\n" + "="*60)
    print("TEST 5: Force Reset")
    print("="*60)
    
    # Force reset (skip cooldown)
    assert ks.reset(authorized_by="test_suite", force=True), "Should force reset successfully"
    
    status = ks.get_status()
    assert status["triggered"] == False, "Should not be triggered"
    assert status["armed"] == False, "Should be disarmed after reset"
    
    print("✅ Force reset successful")
    print("   - System reset and disarmed")


def test_circuit_breaker(ks):
    """Test 6: Circuit Breaker"""
    print("\n" + "="*60)
    print("TEST 6: Circuit Breaker")
    print("="*60)
    
    # Arm
    ks.arm(True)
    
    # Set peak balance
    ks.check(current_balance=1000.0)
    print(f"   - Peak balance set: $1000.00")
    
    # Simulate normal fluctuation (should not trigger)
    triggered = ks.check(current_balance=950.0)  # -5%
    assert not triggered, "Should not trigger at -5%"
    print("✅ -5% drop: No trigger (as expected)")
    
    # Simulate circuit breaker condition (should trigger)
    triggered = ks.check(current_balance=840.0)  # -16%
    assert triggered, "Should trigger at -16%"
    print("✅ -16% drop: Circuit breaker triggered!")
    
    status = ks.get_status()
    print(f"   - Reason: {status['trigger_reason']}")
    
    # Reset for next test
    ks.reset(authorized_by="test_suite", force=True)


def test_daily_loss_limit(ks):
    """Test 7: Daily Loss Limit"""
    print("\n" + "="*60)
    print("TEST 7: Daily Loss Limit")
    print("="*60)
    
    # Arm
    ks.arm(True)
    
    # Set session start balance
    ks.check(current_balance=1000.0)
    print(f"   - Session start: $1000.00")
    
    # Simulate small loss (should not trigger)
    triggered = ks.check(current_balance=970.0)  # -3%
    assert not triggered, "Should not trigger at -3%"
    print("✅ -3% daily loss: No trigger (as expected)")
    
    # Simulate daily loss limit (should trigger)
    triggered = ks.check(current_balance=940.0)  # -6%
    assert triggered, "Should trigger at -6%"
    print("✅ -6% daily loss: Daily loss limit triggered!")
    
    status = ks.get_status()
    print(f"   - Reason: {status['trigger_reason']}")
    
    # Reset for next test
    ks.reset(authorized_by="test_suite", force=True)


def test_emergency_file(ks):
    """Test 8: Emergency File Trigger"""
    print("\n" + "="*60)
    print("TEST 8: Emergency File Trigger")
    print("="*60)
    
    # Arm
    ks.arm(True)
    
    # Create emergency file
    emergency_file = Path(".") / "EMERGENCY_STOP"
    emergency_file.touch()
    print(f"   - Created: {emergency_file}")
    
    # Check should detect file and trigger
    triggered = ks.check()
    assert triggered, "Should trigger when emergency file exists"
    print("✅ Emergency file detected: Kill switch triggered!")
    
    status = ks.get_status()
    print(f"   - Reason: {status['trigger_reason']}")
    
    # Reset for next test (file should be cleaned up)
    ks.reset(authorized_by="test_suite", force=True)
    assert not emergency_file.exists(), "Emergency file should be removed on reset"
    print("✅ Emergency file cleaned up on reset")


def test_history(ks):
    """Test 9: History Logging"""
    print("\n" + "="*60)
    print("TEST 9: History Logging")
    print("="*60)
    
    history = ks.get_history()
    
    assert len(history) >= 3, "Should have at least 3 entries from previous tests"
    print(f"✅ History logged: {len(history)} entries")
    
    # Show last 3 entries
    print("\n   Recent activations:")
    for i, entry in enumerate(history[:3], 1):
        print(f"   {i}. {entry['timestamp']}")
        print(f"      Level {entry['level']}: {entry['reason']}")


def test_graduated_levels(ks):
    """Test 10: All Graduated Levels"""
    print("\n" + "="*60)
    print("TEST 10: Graduated Response Levels")
    print("="*60)
    
    for level in [1, 2, 3, 4]:
        level_enum = Level(level)
        
        # Trigger at this level
        ks.trigger(
            reason=f"Test level {level}",
            level=level,
            triggered_by="test_suite"
        )
        
        status = ks.get_status()
        assert status["trigger_level"] == level, f"Should be at level {level}"
        print(f"✅ Level {level} ({level_enum.name}): OK")
        
        # Reset for next level
        ks.reset(authorized_by="test_suite", force=True)


def test_state_persistence():
    """Test 11: State Persistence"""
    print("\n" + "="*60)
    print("TEST 11: State Persistence")
    print("="*60)
    
    # Create instance and trigger
    ks1 = KillSwitch(workspace=".")
    ks1.trigger(reason="Test persistence", level=3, triggered_by="test_suite")
    
    # Create new instance (should load state)
    ks2 = KillSwitch(workspace=".")
    status = ks2.get_status()
    
    assert status["triggered"] == True, "State should persist across instances"
    assert status["trigger_level"] == 3, "Trigger level should persist"
    assert "Test persistence" in status["trigger_reason"], "Reason should persist"
    
    print("✅ State persists across instances")
    print(f"   - Loaded trigger: {status['trigger_reason']}")
    
    # Cleanup
    ks2.reset(authorized_by="test_suite", force=True)


def cleanup():
    """Clean up test files"""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)
    
    files_to_remove = [
        "kill-switch-state.json",
        "kill-switch-audit.log",
        "EMERGENCY_STOP",
    ]
    
    for filename in files_to_remove:
        filepath = Path(".") / filename
        if filepath.exists():
            filepath.unlink()
            print(f"   - Removed: {filename}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" "*15 + "KILL SWITCH TEST SUITE")
    print("="*70)
    
    try:
        # Run tests
        ks = test_initialization()
        test_arm_disarm(ks)
        test_manual_trigger(ks)
        test_cooldown(ks)
        test_force_reset(ks)
        test_circuit_breaker(ks)
        test_daily_loss_limit(ks)
        test_emergency_file(ks)
        test_history(ks)
        test_graduated_levels(ks)
        test_state_persistence()
        
        # All tests passed
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED!")
        print("="*70)
        print("\nKill switch is working correctly.")
        print("Ready for integration into your trading system.")
        
    except AssertionError as e:
        print("\n" + "="*70)
        print("❌ TEST FAILED")
        print("="*70)
        print(f"Error: {e}")
        return 1
    
    except Exception as e:
        print("\n" + "="*70)
        print("❌ UNEXPECTED ERROR")
        print("="*70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        # Cleanup
        cleanup()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

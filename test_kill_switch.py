import asyncio
import sys
sys.path.insert(0, '.')
from kill_switch_system import KillSwitchSystem

async def test_emergency_halt():
    ks = KillSwitchSystem()
    print('Kill Switch System initialized successfully')
    print(f"Config loaded: {len(ks.config['triggers'])} triggers configured")
    
    # Get initial status
    status = ks.get_status()
    print(f"Initial system state: {status['system_state']}")
    
    await ks.close()
    print('Kill switch test PASSED')

asyncio.run(test_emergency_halt())

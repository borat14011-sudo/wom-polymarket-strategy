import py_clob_client.clob_types as ct
import inspect
print("BalanceAllowanceParams fields:", inspect.signature(ct.BalanceAllowanceParams))
# create instance with defaults
params = ct.BalanceAllowanceParams()
print(params)
# see attributes
print(dir(params))
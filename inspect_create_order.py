import inspect
from py_clob_client.client import ClobClient
from py_clob_client.order_builder.constants import BUY, SELL

print("ClobClient.create_order signature:")
print(inspect.signature(ClobClient.create_order))
print("\nClobClient.create_and_post_order signature:")
print(inspect.signature(ClobClient.create_and_post_order))
print("\nClobClient.post_order signature:")
print(inspect.signature(ClobClient.post_order))

# Let's also see what order_builder constants are available
print("\nBUY:", BUY)
print("SELL:", SELL)
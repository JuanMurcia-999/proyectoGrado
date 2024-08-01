import asyncio

async def problematic_coroutine():
    raise ValueError("Some error")
 
async def another_problematic_coroutine():
    raise KeyError("Another error")
 
async def main():
    results = await asyncio.gather(
        problematic_coroutine(),
        another_problematic_coroutine(),
        return_exceptions=True
    )
 
    for result in results:
        if isinstance(result, Exception):
            print(f"Caught an error: {result}")
 
if __name__ == "__main__":
    asyncio.run(main())
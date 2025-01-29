# Threading.

Threading is a complex topic.
If not handled correctly the application may crash or user's data may get corrupted.

If you do not understand threading, you must stick to a single thread and uniquely
lock the level to ensure no other threads are running in parallel.

The following policies are used in docstrings to document how the function and return behave.

## Call policy

These policies apply from the function's call to when it returns.
If no call policy is given it is assumed to be thread safe.

### Call: Thread safe.

The function can be called from multiple threads without external locking.

### Call: External [shared|unique] lock optional.

The function can be called from multiple threads without external locking.
The function must internally handle locking where needed.
The caller may optionally acquire the external lock to ensure the state is not mutated in another thread.

### Call: External [shared|unique] lock required.

The caller must acquire the external lock before calling the function to ensure the state is not corrupted.

## Return policy

These policies apply to the object returned by the function.
If no return policy is given it is assumed to be independent.

### [Return: ]External [shared] lock optional.

The external lock may be used to ensure the state is not mutated.
The returned object will remain valid without external locks but may be outdated if the state is changed.
The lock must be held from before calling the function until the returned value is no longer needed.

### [Return: ]External [shared] lock required.

The external lock must be used to ensure the state is not mutated.
The returned object may be invalidated if the state is changed.
The lock must be held from before calling the function until the returned value is no longer needed.

## Call and Return policy

If the call and return policy are the same it only needs to be written once.

### External [shared] lock optional.

Applies to both call and return policy.

### External [shared] lock required.

Applies to both call and return policy.

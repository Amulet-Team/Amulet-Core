# Threading.

Threading is a complex topic.
If not handled correctly the application may crash or user's data may get corrupted.

If you do not understand threading, you must stick to a single thread and uniquely
lock the level to ensure no other threads are running in parallel.

The following policies are used in docstrings to document how the function and return behave.

## Lock policy

### Unique mode.

- Any function on the resource can be called in this mode.
- Only the thread holding the lock can use the resource.

### Shared read-only mode.

- Only read functions on the resource can be called in this mode.
- Other threads can acquire the lock in read-only and read mode at the same time.

### Shared read mode.

- Only thread-safe read functions on the resource can be called in this mode.
- Other threads can acquire the lock in read-only mode or read-write mode (not at the same time)

### Shared read-write mode.

- Only thread-safe read or write functions on the resource can be called in this mode.
- Other threads can acquire the lock in read mode or read-write mode.

## Call policy

These policies apply from the function's call to when it returns.
If no call policy is given it is assumed to be not thread safe.

### Call: Thread safe.

The function can be called from multiple threads without external locking.

### Call: External [unique|shared read-only|shared read|shared read-write] lock optional.

The function can be called from multiple threads without external locking.
The function must internally handle locking where needed.
The caller may optionally acquire the external lock to ensure the state is not mutated in another thread.

### Call: External [unique|shared read-only|shared read|shared read-write] lock required.

The caller must acquire the external lock before calling the function to ensure the state is not corrupted.

## Return policy

These policies apply to the object returned by the function.
If no return policy is given it is assumed to be independent.

### [Return: ]External [unique|shared read-only|shared read|shared read-write] lock optional.

The external lock may be used to ensure the state is not mutated.
The returned object will remain valid without external locks but may be outdated if the state is changed.
The lock must be held from before calling the function until the returned value is no longer needed.

### [Return: ]External [unique|shared read-only|shared read|shared read-write] lock required.

The external lock must be used to ensure the state is not mutated.
The returned object may be invalidated if the state is changed.
The lock must be held from before calling the function until the returned value is no longer needed.

## Call and Return policy

If the call and return policy are the same it only needs to be written once.

### External [unique|shared read-only|shared read|shared read-write] lock optional.

Applies to both call and return policy.

### External [unique|shared read-only|shared read|shared read-write] lock required.

Applies to both call and return policy.

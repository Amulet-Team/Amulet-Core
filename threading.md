# Threading.

Threading is a complex topic.
If not handled correctly the application may crash or user's data may get corrupted.

If you do not understand threading, you must stick to a single thread and uniquely
lock the level to ensure no other threads are running in parallel.

The following policies are used in docstrings to document how the function and return behave.

## Code policy

These policies are included in function docstrings to specify if and how the associated lock must be acquired.
If no call policy is given it should be assumed the associated lock must be acquired in unique read-write mode.

### [[Call:|Return:]](#Code-policy-scope) Thread safe.

The code can be executed from multiple threads without external locking.

### [[Call:|Return:]](#Code-policy-scope) [(Read|ReadWrite)](#ThreadAccessMode):[(Unique|SharedReadOnly|SharedReadWrite)](#ThreadShareMode) lock required. 

The caller must acquire the associated lock in a compatible mode for the defined scope. 
This ensures that the state is not corrupted by another thread.

### [[Call:|Return:]](#Code-policy-scope) [(Read|ReadWrite)](#ThreadAccessMode):[(Unique|SharedReadOnly|SharedReadWrite)](#ThreadShareMode) lock optional. 

This indicates that a more restrictive lock mode may be used.
The caller may acquire the associated lock in a compatible mode to ensure the state is not mutated in another thread.
This is used in cases where the state will not be corrupted but may become outdated if other threads mutate it.

### Unique lock (required|optional).

Equivalent to ReadWrite:Unique
This is the normal lock behaviour.

### Shared lock (required|optional).

Equivalent to Read:SharedReadOnly
This is the normal shared lock behaviour.

## Code policy scope

The code policy can be optionally prefixed with a scope.
If no scope is defined it defaults to the `Return` scope.

### Call

If the code policy is prefixed with `Call:`, the policy applies from when the function is called until when it returns.

### Return

If the code policy is prefixed with `Return:`, the policy applies from when the function is called until when the
return is no longer used.

## ThreadAccessMode

Defines what a function and thread can do. 

### Read

When used in relation to code, it means that the code only reads the associated state.
The code's lock must be acquired in Read or ReadWrite mode to execute it.

When a thread acquires a lock in Read mode it may only execute associated code that needs Read access.

### ReadWrite

When used in relation to code, it means that the code can read and write the associated state.
The code's lock must be acquired in ReadWrite mode to execute it.

When a thread acquires a lock in ReadWrite mode it may execute associated code that needs Read or ReadWrite access.

## ThreadShareMode

Defines the access mode that other threads may use in parallel.

### Unique

When used in relation to code, it means that it cannot be executed in parallel with associated code.
The code's lock must be acquired in Unique mode.

### SharedReadOnly

When used in relation to code, it means that it can only be executed in parallel with associated code that needs Read mode.
The code's lock must be acquired in Unique or SharedReadOnly mode.

### SharedReadWrite

When used in relation to code, it means that it can be executed in parallel with associated code that needs Read or ReadWrite mode.
The code's lock must be acquired in Unique, SharedReadOnly or SharedReadWrite mode.

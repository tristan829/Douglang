---
title: Control Flow
permalink: /docs/control_flow/
---

# Control Flow

Douglang doesn't have much control flow. Our scientists are still figuring out what "structured programming" even means. That means no functions or fancy loops. I'm sure we'll get them eventually, it's only a matter of time.

But let's focus on the present, because the present is a gift, that's why it's called the present.

To loop, say `loop`. Confusing, I know. Don't worry, I believe in you.
```
loop [
    tts "I'm going to say this forever."
]
```
Loops go forever. Why do they go forever? Because if they didn't loop, they wouldn't be a `loop`. You can end a loop with `break`:
```
loop [
    tts "What is my purpose? Just to loop? Forever?"
    break // Oh, thank you.
]
```
Except now it doesn't loop and therefore doesn't deserve to be called `loop`. We can fix this with predictions. 
```
prediction (Doug) = "Douglas Wreden" [
    Believers win [
        tts "Hey Doug"
    ]
]
```


And, what's that? `=` is for assignment? No, This is Douglang. We use `set` for assignment. That frees up `=` for conditionals, instead of the *disgusting* and *vulgar* `==`.

The `Believers win` block runs whenever the condition is true, because the Believers believe it will evaluate to true, and they won. The same would happen with a `Doubters win` block, because the Doubters believe it will evaluate to false.

Combine that with `loop` and now you have a loop that doesn't go on forever. I don't know why you would want that, because loops going forever is cool.

```
// Laundry alarm
Doug set 5
loop [
    Bald set "Laundry in " +set (Doug) +set "." tts
    Doug -set 1
    prediction (Doug) = 0 [
        Believers win [
            break
        ]
    ]
]
tts "LAUNDRY!!!!!!!" 
```

# Algo-Sonic

A sorting and searching algorithm visualizer that also turns each step into sound. Bars on screen show the array, and every comparison, swap, or visit plays a note, so you can literally hear how an algorithm behaves.

## What it does

Pick an algorithm (bubble sort, insertion sort, selection sort, quick sort, merge sort, heap sort, linear search, or binary search) and watch it run against a random array. Each meaningful action lights up bars on screen and plays a tone whose pitch reflects the value involved. Fast, chaotic algorithms sound busy. Clean divide and conquer algorithms sound rhythmic. You start to hear the difference between O(n^2) and O(n log n), not just read about it.

## Project layout

```
main.py         the app loop: input, timing, and wiring everything together
algorithms.py   the sorting/search algorithms themselves, as generators
audio.py        turns array values into musical notes and synthesizes them
visuals.py      draws the array as colored bars
```

## The core idea: algorithms as generators

The most important design decision in this project is in `algorithms.py`. Each algorithm is written as a normal implementation, except instead of just comparing or swapping silently, it does this:

```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(n - i - 1):
            yield ("compare", j, j + 1)
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                yield ("swap", j, j + 1)
```

Using `yield` instead of `return` makes `bubble_sort` a generator function. Calling `bubble_sort(arr)` does not run any sorting yet, it just creates a generator object. Each call to `next(generator)` resumes the function until it hits the next `yield`, hands back that value, and pauses again.

This means the algorithm can describe its own steps one at a time, without knowing anything about pygame, drawing, or sound. It just reports what it is doing. Whoever is driving the generator decides how fast to pull steps and what to do with each one.

Every algorithm only ever yields one of four event shapes:

- `("compare", i, j)` looking at two indices to compare them
- `("swap", i, j)` swapping the values at two indices
- `("visit", i)` inspecting a single index (used by the search algorithms)
- `("set", i, val)` overwriting an index directly (merge sort needs this since it rebuilds from a temporary buffer instead of swapping in place)

Quick sort and merge sort call themselves recursively, and use `yield from` so that events produced deep inside the recursion still flow straight up to whoever is driving the top level generator.

## The main loop: turning steps into a fixed pace

`main.py` holds an `App` class that owns the current array, the current algorithm's generator, and the game loop. On every step, it does this:

```python
event = next(self.gen)
kind = event[0]
```

and dispatches based on the tag, updating which bars are "active" and telling `audio.py` to play a note for each index involved. When the generator runs out of steps, Python raises `StopIteration`, which the code catches to mark the algorithm finished. No extra "am I done" flag is needed, the generator protocol already gives you that.

Algorithms can produce thousands of steps, and you do not want sorting speed tied to your monitor's refresh rate. So the loop uses a fixed timestep accumulator:

```python
self.step_accum_ms += dt
step_interval = 1000 / self.speed
while self.step_accum_ms >= step_interval:
    self.step_accum_ms -= step_interval
    self.step()
```

Every real frame adds elapsed milliseconds into a bucket. The loop drains that bucket in fixed-size chunks, running one algorithm step per chunk. If the chosen speed is high, several steps can happen in a single frame. If it is low, several frames can pass before the next step happens. Speed becomes an independent setting instead of being locked to frame rate.

## Turning values into sound

`audio.py` maps array values to musical notes instead of raw frequencies. The scale used is a C major pentatonic scale spread across three octaves. Pentatonic scales have no dissonant intervals, so any two notes played close together still sound pleasant, no matter how erratic the algorithm's access pattern is. A straight linear pitch mapping would sound noisy during fast comparisons, the pentatonic scale keeps it musical.

Each note is synthesized directly with numpy as a sine or square wave, faded in and out over a few milliseconds to avoid clicking, then handed to pygame's mixer as a sound. Since there are only a limited number of possible (event type, note) combinations, each sound is generated once and cached, so repeated notes do not re-synthesize audio every time.

The pitch for a given value is chosen by mapping its position within the current array's minimum and maximum onto an index in the scale, so pitch always reflects relative magnitude within that specific array.

## Drawing the bars

`visuals.py` is the simplest file. Every frame it redraws the whole array as bars, with height proportional to value. Bars involved in the current step are highlighted, and the whole array turns a different color once the algorithm is finished. There is no animation between frames, the screen always reflects the current, live state of the array.

## How it all fits together each frame

On every frame, `main.py`:

1. Reads keyboard input (play/pause, reset, change algorithm, change speed, toggle info panel)
2. Drains the step accumulator, which pulls events from the algorithm generator, mutates the array, and triggers audio
3. Calls `visuals.draw_bars` to redraw the array based on its current state
4. Draws the heads up display and, optionally, the algorithm description panel

Audio and visuals never talk to each other directly. They are both just reacting independently to the same stream of events coming out of `main.step()`, which is what keeps the algorithm code itself completely free of any rendering or sound logic.

## Controls

- `space` play or pause
- `r` reset with a new random array
- `left` / `right` or `a` / `d` switch algorithm
- `up` / `down` or `w` / `s` change speed
- `i` toggle the algorithm info panel
- `esc` quit

## Running it

```
pip install -r requirements.txt
python main.py
```

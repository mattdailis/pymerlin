# Using Current Value in an Effect Model

:::{warning}
This page is under construction. Please bear with us as we port
our [Java tutorial](https://nasa-ammos.github.io/aerie-docs/tutorials/mission-modeling/introduction/) to python.
:::

Now that we have our magnetometer resources, we need to build an activity that changes the `MagDataMode` for us (
since `MagDataRate` is a derived resource, we shouldn't have to touch it) and changes the overall SSR `recording_rate` to
reflect the magnetometer's data rate change. This activity, which we'll call `change_mag_mode`, only needs one parameter
of type `MagDataCollectionMode` to allow the user to request a change to the mode. Let's give that parameter a default
value of `LOW_RATE`.

In the effect model for this activity (which we'll call `run()` by convention), we can use the `set()` method in
the `DiscreteEffects` class to change the `MagDataMode` to the value provided by our mode parameter. The computation of
the change to the `recording_rate` caused by the mode change is a little tricky because we need to know both the value of
the `MagDataRate` before and after the mode change. Once we know those value, we can subtract the old value from the new
value to get the net increase to the `recording_rate`. If the new value happens to be less than the old value, our answer
will be negative, but that should be ok as long as we use the `increase()` method when effecting the `recording_rate`
resource.

We can get the current value of a resource with a static method called `currentValue()` available in the `Resources`
class. For our case here, we want to get the current value of the `MagDataRate` **before** we actually change the mode
to the requested value, so we have to be a little careful about the order of operations within our effect model. The
resulting activity type and its effect model should look something like this:

```java
@Model.ActivityType()
async def change_mag_mode(model, mode: MagDataCollectionMode = MagDataCollectionMode.LOW_RATE):
    current_rate = model.data_model.MagDataRate.get()
    new_rate = mode.get_data_rate()
    // Divide by 10^3 for kbps->Mbps conversion
    model.data_model.recording_rate += (new_rate-current_rate)/1.0e3
    model.data_model.MagDataMode.set(mode)
```

Looking at our new activity definition, you can see how we use the `increase()` effect on `recording_rate` to "increase"
the data rate based on the net data change from the old rate. You may also notice a magic number where we do a unit
conversion from `kbps` to `Mbps`, which isn't ideal. Later on in this tutorial, we will introduce a "Unit Aware"
resource framework that will help a bit with conversions like these if desired.

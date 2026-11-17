package com.steelwater.addonlauncher.tests;

import android.app.Activity;
import android.app.Application;
import android.app.Instrumentation;
import android.content.Intent;
import android.content.pm.ActivityInfo;
import android.net.Uri;
import android.os.Bundle;
import android.os.SystemClock;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.TextView;
import java.lang.reflect.Method;
import java.util.function.BooleanSupplier;

public final class ImportTests extends Instrumentation implements Application.ActivityLifecycleCallbacks {
    private static final String MAIN = "com.steelwater.addonlauncher.MainActivity";
    private static final Uri SOURCE = Uri.parse("content://com.steelwater.addonlauncher.tests.slow/valid");
    private volatile Activity current;
    private volatile boolean active;

    @Override public void onCreate(Bundle args) { super.onCreate(args); start(); }
    @Override public void onStart() {
        Bundle result = new Bundle();
        Application app = (Application) getTargetContext().getApplicationContext();
        app.registerActivityLifecycleCallbacks(this);
        try {
            check(getTargetContext().getPackageManager().getLaunchIntentForPackage("com.mojang.minecraftpe") == null,
                    "Run on an emulator without Minecraft; this suite checks the accurate retry path");
            Intent intent = new Intent().setClassName(getTargetContext(), MAIN).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivitySync(intent);
            await(() -> current != null && active, "Launcher did not resume");
            verifyRotation(false);
            verifyRotation(true);
            verifyBackgroundCompletion();
            result.putString("stream", "PASS: slow import survives rotation; one source read; accurate missing-Minecraft retry; no repeated import after another rotation; corrupt ZIP recovers after rotation; background completion waits for resume\n");
            finish(Activity.RESULT_OK, result);
        } catch (Exception | AssertionError e) {
            result.putString("stream", "FAIL: " + e + "\n");
            finish(Activity.RESULT_CANCELED, result);
        } finally {
            getContext().getContentResolver().call(SOURCE, "release", null, null);
            app.unregisterActivityLifecycleCallbacks(this);
            if (current != null) runOnMainSync(() -> current.finish());
        }
    }
    private void verifyRotation(boolean invalid) throws Exception {
        getContext().getContentResolver().call(SOURCE, "reset", null, null);
        Activity original = current;
        Method select = original.getClass().getDeclaredMethod("onActivityResult", int.class, int.class, Intent.class);
        select.setAccessible(true);
        runOnMainSync(() -> {
            try { select.invoke(original, 10, Activity.RESULT_OK, new Intent().setData(invalid ? SOURCE.buildUpon().path("invalid").build() : SOURCE)); }
            catch (Exception e) { throw new AssertionError(e); }
        });
        await(() -> sourceOpens() == 1, "Source pipe was not opened");
        check(text().equals("Preparing the add-on…"), "Import did not enter preparing state");
        rotate();
        check(text().equals("Preparing the add-on…"), "Rotation lost pending status");
        check(!enabled(), "Rotation enabled a second selection during the copy");
        getContext().getContentResolver().call(SOURCE, "release", null, null);
        await(() -> !text().equals("Preparing the add-on…"), "Import stayed stuck after rotation");
        String completed = text();
        check(completed.startsWith(invalid ? "Could not prepare the add-on:" : "Minecraft was not found"), "Wrong completion state: " + completed);
        check(enabled(), "Retry was not enabled");
        rotate();
        check(text().equals(completed), "Another rotation changed the completed result");
        check(enabled() && sourceOpens() == 1, "Rotation repeated the import or disabled retry");
    }
    private void rotate() {
        Activity before = current;
        int orientation = before.getResources().getConfiguration().orientation == 1
                ? ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE : ActivityInfo.SCREEN_ORIENTATION_PORTRAIT;
        runOnMainSync(() -> before.setRequestedOrientation(orientation));
        await(() -> current != before && active, "Orientation change did not recreate the Activity");
        waitForIdleSync();
    }
    private void verifyBackgroundCompletion() throws Exception {
        getContext().getContentResolver().call(SOURCE, "reset", null, null);
        Activity activity = current;
        Method select = activity.getClass().getDeclaredMethod("onActivityResult", int.class, int.class, Intent.class);
        select.setAccessible(true);
        runOnMainSync(() -> {
            try { select.invoke(activity, 10, Activity.RESULT_OK, new Intent().setData(SOURCE)); }
            catch (Exception e) { throw new AssertionError(e); }
        });
        await(() -> sourceOpens() == 1, "Background fixture was not opened");
        runOnMainSync(() -> activity.moveTaskToBack(true));
        await(() -> !active, "Launcher did not pause");
        getContext().getContentResolver().call(SOURCE, "release", null, null);
        // Inspect only to establish that completion really occurred while detached.
        java.lang.reflect.Field field = activity.getClass().getDeclaredField("work");
        field.setAccessible(true);
        await(() -> {
            boolean[] done = new boolean[1];
            runOnMainSync(() -> {
                try {
                    Object work = field.get(activity);
                    check(work != null, "Paused Activity consumed the result");
                    java.lang.reflect.Field completed = work.getClass().getDeclaredField("done");
                    completed.setAccessible(true);
                    done[0] = completed.getBoolean(work);
                } catch (Exception e) { throw new AssertionError(e); }
            });
            return done[0];
        }, "Copy did not finish while paused");
        check(text().equals("Preparing the add-on…"), "Paused Activity handled completion");
        getTargetContext().startActivity(new Intent().setClassName(getTargetContext(), MAIN)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_REORDER_TO_FRONT));
        await(() -> active && text().startsWith("Minecraft was not found"), "Resume did not deliver completed import");
        check(enabled() && sourceOpens() == 1, "Resume did not offer retry or restarted the copy");
    }
    private int sourceOpens() { return getContext().getContentResolver().call(SOURCE, "status", null, null).getInt("opens"); }
    private String text() {
        String[] value = new String[1];
        runOnMainSync(() -> value[0] = status(current.getWindow().getDecorView()).getText().toString());
        return value[0];
    }
    private boolean enabled() {
        boolean[] value = new boolean[1];
        runOnMainSync(() -> value[0] = button(current.getWindow().getDecorView()).isEnabled());
        return value[0];
    }
    private TextView status(View view) {
        if (view instanceof TextView && view.getAccessibilityLiveRegion() == View.ACCESSIBILITY_LIVE_REGION_POLITE) return (TextView) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) { TextView found = status(group.getChildAt(i)); if (found != null) return found; }
        }
        return null;
    }
    private Button button(View view) {
        if (view instanceof Button) return (Button) view;
        if (view instanceof ViewGroup) {
            ViewGroup group = (ViewGroup) view;
            for (int i = 0; i < group.getChildCount(); i++) { Button found = button(group.getChildAt(i)); if (found != null) return found; }
        }
        return null;
    }
    private static void await(BooleanSupplier condition, String message) {
        long deadline = SystemClock.uptimeMillis() + 15000;
        while (!condition.getAsBoolean() && SystemClock.uptimeMillis() < deadline) SystemClock.sleep(50);
        check(condition.getAsBoolean(), message);
    }
    private static void check(boolean value, String message) { if (!value) throw new AssertionError(message); }
    @Override public void onActivityCreated(Activity activity, Bundle state) { if (activity.getClass().getName().equals(MAIN)) current = activity; }
    @Override public void onActivityResumed(Activity activity) { if (activity == current) active = true; }
    @Override public void onActivityPaused(Activity activity) { if (activity == current) active = false; }
    @Override public void onActivityStarted(Activity activity) { }
    @Override public void onActivityStopped(Activity activity) { }
    @Override public void onActivitySaveInstanceState(Activity activity, Bundle state) { }
    @Override public void onActivityDestroyed(Activity activity) { }
}

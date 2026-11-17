package com.steelwater.addonlauncher.tests;

import android.app.Instrumentation;
import android.app.Activity;
import android.content.ContentResolver;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import java.io.File;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.UUID;

public final class ProviderTests extends Instrumentation {
    @Override public void onCreate(Bundle args) { super.onCreate(args); start(); }
    @Override public void onStart() {
        Bundle result = new Bundle();
        File fixture = new File(getTargetContext().getCacheDir(), UUID.randomUUID() + ".mcaddon");
        try {
            byte[] expected = new byte[]{80, 75, 3, 4, 7, 8, 9};
            Files.write(fixture.toPath(), expected);
            Uri uri = Uri.parse("content://com.steelwater.addonlauncher.files/" + fixture.getName());
            ContentResolver resolver = getTargetContext().getContentResolver();
            try (InputStream stream = resolver.openInputStream(uri)) {
                for (byte b : expected) check(stream.read() == (b & 255), "Shared bytes differ");
                check(stream.read() == -1, "Unexpected trailing bytes");
            }
            try (Cursor cursor = resolver.query(uri, new String[]{OpenableColumns.SIZE, OpenableColumns.DISPLAY_NAME}, null, null, null)) {
                check(cursor.moveToFirst(), "Missing metadata");
                check(cursor.getLong(0) == expected.length, "Wrong size");
                check(cursor.getString(1).endsWith(".mcaddon"), "Extension not retained");
            }
            boolean refused = false;
            try { resolver.openFileDescriptor(uri, "w").close(); } catch (java.io.FileNotFoundException e) { refused = true; }
            check(refused, "Provider allowed a write");
            refused = false;
            try { resolver.openInputStream(Uri.parse("content://com.steelwater.addonlauncher.files/../private.mcaddon")).close(); }
            catch (java.io.FileNotFoundException e) { refused = true; }
            check(refused, "Provider accepted an unknown path");
            result.putString("stream", "PASS: byte integrity, filename/size metadata, write rejection, unknown-path rejection\n");
            finish(Activity.RESULT_OK, result);
        } catch (Exception | AssertionError e) {
            result.putString("stream", "FAIL: " + e + "\n");
            finish(Activity.RESULT_CANCELED, result);
        } finally { fixture.delete(); }
    }
    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}

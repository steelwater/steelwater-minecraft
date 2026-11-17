package com.steelwater.addonlauncher.tests;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;
import java.io.ByteArrayOutputStream;
import java.io.FileNotFoundException;
import java.io.OutputStream;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;

// Test APK only: a pipe whose EOF is held until the test releases it after rotation.
public final class SlowAddonProvider extends ContentProvider {
    private volatile CountDownLatch release = new CountDownLatch(1);
    private volatile int opens;
    @Override public boolean onCreate() { return true; }
    @Override public String getType(Uri uri) { return "application/octet-stream"; }
    @Override public Cursor query(Uri uri, String[] projection, String selection, String[] args, String sort) {
        MatrixCursor cursor = new MatrixCursor(new String[]{OpenableColumns.DISPLAY_NAME});
        cursor.addRow(new Object[]{"slow.mcaddon"});
        return cursor;
    }
    @Override public Bundle call(String method, String arg, Bundle extras) {
        if (method.equals("reset")) { release = new CountDownLatch(1); opens = 0; }
        if (method.equals("release")) release.countDown();
        Bundle result = new Bundle();
        result.putInt("opens", opens);
        return result;
    }
    @Override public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (!mode.equals("r")) throw new FileNotFoundException("Read only");
        try {
            ParcelFileDescriptor[] pipe = ParcelFileDescriptor.createPipe();
            CountDownLatch gate = release;
            opens++;
            new Thread(() -> {
                try (OutputStream output = new ParcelFileDescriptor.AutoCloseOutputStream(pipe[1])) {
                    ByteArrayOutputStream bytes = new ByteArrayOutputStream();
                    try (ZipOutputStream zip = new ZipOutputStream(bytes)) {
                        zip.putNextEntry(new ZipEntry("fixture.txt"));
                        zip.write(new byte[]{1, 2, 3});
                        zip.closeEntry();
                    }
                    output.write(uri.getLastPathSegment().equals("invalid") ? new byte[]{1, 2, 3} : bytes.toByteArray());
                    output.flush();
                    if (!gate.await(20, TimeUnit.SECONDS)) throw new java.io.IOException("Test did not release pipe");
                } catch (Exception e) { android.util.Log.e("SlowAddonProvider", "Fixture failed", e); }
            }, "slow-addon-fixture").start();
            return pipe[0];
        } catch (java.io.IOException e) { throw new FileNotFoundException(e.toString()); }
    }
    @Override public Uri insert(Uri uri, ContentValues values) { throw new UnsupportedOperationException(); }
    @Override public int update(Uri uri, ContentValues values, String selection, String[] args) { throw new UnsupportedOperationException(); }
    @Override public int delete(Uri uri, String selection, String[] args) { throw new UnsupportedOperationException(); }
}

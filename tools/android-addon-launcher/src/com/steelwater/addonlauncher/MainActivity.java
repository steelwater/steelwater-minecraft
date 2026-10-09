package com.steelwater.addonlauncher;

import android.app.Activity;
import android.content.ClipData;
import android.content.Intent;
import android.database.Cursor;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.util.Locale;
import java.util.UUID;
import java.util.zip.ZipFile;

public final class MainActivity extends Activity {
    private TextView status;
    private Button choose;
    private static final int PICK = 10;
    private static final long LIMIT = 256L * 1024 * 1024;

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        ScrollView scroll = new ScrollView(this);
        LinearLayout layout = new LinearLayout(this);
        layout.setOrientation(LinearLayout.VERTICAL);
        int padding = (int) (24 * getResources().getDisplayMetrics().density);
        layout.setPadding(padding, padding, padding, padding);
        scroll.addView(layout);
        scroll.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                    insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets;
        });
        TextView title = new TextView(this);
        title.setText("Open an add-on in Minecraft");
        title.setTextSize(26);
        layout.addView(title);
        TextView description = new TextView(this);
        description.setText("Choose a .mcaddon from Downloads or Drive. Minecraft will handle the import.\n\nThis unofficial helper does not change your worlds or need access to Minecraft’s folders.");
        description.setTextSize(18);
        description.setPadding(0, padding, 0, padding);
        layout.addView(description);
        choose = new Button(this);
        choose.setText("Choose .mcaddon");
        layout.addView(choose);
        status = new TextView(this);
        status.setTextSize(16);
        status.setPadding(0, padding, 0, padding);
        status.setAccessibilityLiveRegion(View.ACCESSIBILITY_LIVE_REGION_POLITE);
        status.setText(state == null ? "Ready. Minecraft must be installed in this Android profile." : state.getString("status", "Ready."));
        layout.addView(status);
        choose.setOnClickListener(v -> {
            Intent picker = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            picker.addCategory(Intent.CATEGORY_OPENABLE);
            // Some document providers label mcaddon as ZIP; filter by filename after selection.
            picker.setType("*/*");
            try { startActivityForResult(picker, PICK); }
            catch (RuntimeException e) { status.setText("Android could not open the file picker: " + e.getMessage()); }
        });
        setContentView(scroll);
    }
    @Override protected void onSaveInstanceState(Bundle state) {
        state.putString("status", status.getText().toString());
        super.onSaveInstanceState(state);
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request != PICK) return;
        if (result != RESULT_OK || data == null || data.getData() == null) {
            status.setText("No file selected. You can try again.");
            return;
        }
        Uri source = data.getData();
        choose.setEnabled(false);
        status.setText("Preparing the add-on…");
        new Thread(() -> prepare(source), "addon-copy").start();
    }
    private void prepare(Uri source) {
        File copy = null;
        try {
            String name = null;
            try (Cursor c = getContentResolver().query(source, new String[]{OpenableColumns.DISPLAY_NAME}, null, null, null)) {
                if (c != null && c.moveToFirst()) name = c.getString(0);
            }
            if (name == null || !name.toLowerCase(Locale.ROOT).endsWith(".mcaddon")) {
                throw new java.io.IOException("Please select a file whose name ends in .mcaddon.");
            }
            // Expired copies belong to this helper only. Keep recent files for Minecraft's asynchronous read.
            File[] old = getCacheDir().listFiles();
            if (old != null) for (File f : old) {
                if (f.getName().matches("[a-f0-9-]{36}\\.mcaddon") && System.currentTimeMillis() - f.lastModified() > 86400000L) f.delete();
            }
            copy = new File(getCacheDir(), UUID.randomUUID() + ".mcaddon");
            try (InputStream input = getContentResolver().openInputStream(source);
                 OutputStream output = Files.newOutputStream(copy.toPath())) {
                if (input == null) throw new java.io.IOException("The selected file could not be read.");
                byte[] buffer = new byte[32768];
                long total = 0;
                int n;
                while ((n = input.read(buffer)) != -1) {
                    total += n;
                    if (total > LIMIT) throw new java.io.IOException("This test helper supports files up to 256 MB.");
                    output.write(buffer, 0, n);
                }
            }
            try (ZipFile zip = new ZipFile(copy)) {
                if (!zip.entries().hasMoreElements()) throw new java.io.IOException("The archive is empty.");
            }
            Uri uri = Uri.parse("content://com.steelwater.addonlauncher.files/" + copy.getName());
            runOnUiThread(() -> launch(uri));
        } catch (Exception e) {
            if (copy != null) copy.delete();
            String message = "Could not prepare the add-on: " + e.getMessage();
            runOnUiThread(() -> { choose.setEnabled(true); status.setText(message); });
        }
    }
    private void launch(Uri uri) {
        if (isDestroyed() || isFinishing()) return;
        choose.setEnabled(true);
        // Discover the installed launch activity rather than hardcoding Minecraft's activity class.
        Intent entry = getPackageManager().getLaunchIntentForPackage("com.mojang.minecraftpe");
        if (entry == null) {
            status.setText("Minecraft was not found in this Android profile. Install or enable the Google Play version, then choose the add-on again.");
            return;
        }
        Intent open = new Intent(Intent.ACTION_VIEW);
        open.setComponent(entry.getComponent());
        open.setDataAndType(uri, "application/octet-stream");
        open.setClipData(ClipData.newRawUri("Minecraft add-on", uri));
        open.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
        try {
            startActivity(open);
            status.setText("Sent to Minecraft. Check its import notification; opening Minecraft alone does not confirm a successful import.");
        } catch (RuntimeException e) {
            status.setText("Minecraft could not open the add-on: " + e.getMessage());
        }
    }
}

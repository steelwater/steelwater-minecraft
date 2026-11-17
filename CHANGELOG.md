# Changelog

Meaningful changes follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- Source and build instructions for the optional Android add-on launcher, with provider and lifecycle instrumentation tests.

### Fixed

- Pending Android add-on imports reconnect after screen rotation, keep selection disabled during copying, and consume the result once from a resumed screen.
- Restoring an interrupted import without its in-memory operation shows an accurate retry message.

The launcher changes are tracked in PR #2 and are separate from Underground Tech Pack Milestone 1. The published `addon-launcher-v0.1.0` artifact predates these fixes and remains unchanged.

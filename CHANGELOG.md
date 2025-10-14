# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-10-14

### Changed

- Moved `hangman.Hangman.lazy_launch()` from a class method to a top-level
  function (now named `hangman.play_hangman()`).

### Fixed

- Fixed issue where endless mode was not working on Hangman.

## [0.2.0] - 2025-10-14

### Added

- **Magic 8 Ball** (`magic8ball`): based on the toy of the same name.
- **Endless mode** (`-e`, `--endless`) for `hangman` and `magic8ball`.

## [0.1.0] - 2025-10-13

### Added

- Base application.
- **Hangman** (`hangman`): the classic guessing game, implemented for the
  command-line.

[0.2.1]: https://github.com/mellowghostyx/pygames/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/mellowghostyx/pygames/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mellowghostyx/pygames/releases/tag/v0.1.0

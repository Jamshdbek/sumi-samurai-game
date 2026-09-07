# Publishing Sumi on CrazyGames

Two commands produce everything the developer portal asks for:

```bash
npm run package   # release/sumi-crazygames.zip  — the game bundle
npm run covers    # release/covers/*.png         — the three cover images
```

`release/` is gitignored; both commands rebuild it from scratch.

## What `npm run package` does

1. `vite build` into `dist/`.
2. Drops any file in `dist/assets` whose name appears nowhere in the built
   HTML. The repo keeps source sheets and retired art next to the live art;
   this is what stops them riding along in the upload.
3. Checks the bundle against the portal's limits and refuses to call itself
   ready if any of these fail:
   - absolute asset paths (their CDN serves the game from a nested path, so
     `/assets/…` would 404)
   - any remote resource other than `sdk.crazygames.com`
   - the four SDK calls a review looks for
   - 250 MB / 1500 files / 50 MB initial download
4. Zips `dist/` with `index.html` at the archive root.

Current bundle: **73 files, 3.6 MB unpacked, 2.8 MB zipped** — comfortably
inside the 20 MB initial-download threshold that keeps the game eligible for
the mobile home page.

## SDK integration

All of it lives in `window.GameEvents` near the top of the inline script in
[index.html](index.html), and every call is wrapped so a missing SDK is never
fatal — the game runs identically off-portal.

| Call | Fired when |
| --- | --- |
| `SDK.init()` | boot, raced against a 3 s timeout so Play is never blocked |
| `game.loadingStart()` / `loadingStop()` | around the art preload |
| `game.gameplayStart()` / `gameplayStop()` | every run start, pause, death and menu |
| `game.happytime()` | a chapter is cleared |
| `ad.requestAd('midgame')` | between chapters, via `withAdBreak()` |
| `data.*` | the save, tier 1 of three (SDK → localStorage → memory) |
| `user.getUser()` | fills the run board with the player's real name |

### Sitelock

On, at the top of the script. The host test is the one CrazyGames publishes:
`crazygames` has to be one of the last three labels of the hostname, which
covers every regional domain and their capacitor:// app WebView. localhost,
`file://` and private LAN addresses are allowed so local and on-device testing
still work.

To publish the same build elsewhere, add the host to `SITELOCK.EXTRA_HOSTS`;
to switch the lock off, set `SITELOCK.ENABLED = false`.

## Cover images

`npm run covers` renders [tools/cover.html](tools/cover.html) with headless
Chrome at the three sizes the portal requires:

| File | Size | Ratio |
| --- | --- | --- |
| `sumi-landscape-1920x1080.png` | 1920×1080 | 16:9 |
| `sumi-portrait-800x1200.png` | 800×1200 | 2:3 |
| `sumi-square-800x800.png` | 800×800 | 1:1 |

All three are built from the game's own art — the same four parallax plates,
the same day tileset, the same samurai sheet — so the store page and the game
read as one thing. No borders, no text but the title. Edit `tools/cover.html`
and re-run to change the composition.

## Still to do by hand in the portal

- **Preview videos.** Two are mandatory: 1080p 16:9 and 1080p 2:3, silent,
  15–20 s, opening on the static cover frame, no cursor and no black bars.
  These have to be screen-recorded from real play.
- Title, description, tags and controls text.
- Confirm the two ad placements read as intended once ads are live; only
  midgame is wired up, there is no rewarded placement.

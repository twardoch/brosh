# TODO

Modernization pass is done (see CHANGELOG). Remaining ideas, roughly by effort:

## Tests / coverage
- [ ] Mock a Playwright `page` to cover `capture.py` scrolling logic (currently ~19%).
- [ ] Mock `BrowserScreenshotTool.capture` to cover `tool.py` orchestration.
- [ ] Add an integration test that captures a `file://` local HTML fixture end-to-end (needs Chrome; mark `@pytest.mark.integration`).

## Features
- [ ] Concurrent capture for multi-frame operations.
- [ ] Capture a specific region/element only as a bounding capture.
- [ ] PDF export format.
- [ ] Custom user-agent and proxy support.

## Docs / ops
- [ ] Publish the `docs/` site to GitHub Pages (enable Pages on the `docs/` folder).
- [ ] Document Docker deployment for headless Linux capture.
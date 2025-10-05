$env:PYO3_PYTHON = (Resolve-Path -LiteralPath ".\src-tauri\pyembed\python\python.exe").Path

uv pip install `                                                                           
    --exact `
    --python=".\src-tauri\pyembed\python\python.exe" `
    --reinstall-package=classtop `
    .\src-tauri

npm run -- tauri build --config="src-tauri/tauri.bundle.json" -- --profile bundle-release
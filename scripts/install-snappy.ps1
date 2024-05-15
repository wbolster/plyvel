$SNAPPY_VERSION="1.1.9"

# Check env
if (-not (Test-Path env:CIBW_ARCHS_WINDOWS)) { $env:CIBW_ARCHS_WINDOWS = "AMD64" }
if ($env:CIBW_ARCHS_WINDOWS -eq "x86") {
    $arch="Win32"
} elseif ($env:CIBW_ARCHS_WINDOWS -eq "AMD64") {
    $arch="x64"
} else {
    $arch=""
    Write-Output "not support arch $env:CIBW_ARCHS_WINDOWS"
    exit
}


# Prepare snappy source code
$url="https://codeload.github.com/google/snappy/tar.gz/$SNAPPY_VERSION"
$repo="C:\opt"
$output="snappy.tar.gz"

mkdir $repo -ea 0; Set-Location $repo
Invoke-WebRequest -Uri $url -OutFile $output
tar -xzf $output
Set-Location snappy-*

# Compile snappy
$INSTALL_PREFIX="C:\local"

mkdir build -ea 0; Set-Location build
cmake -G "Visual Studio 16 2019" -A $arch `
    -DCMAKE_INSTALL_PREFIX="$INSTALL_PREFIX" `
    -DBUILD_SHARED_LIBS=ON `
    -DCMAKE_POSITION_INDEPENDENT_CODE=ON `
    -DSNAPPY_BUILD_BENCHMARKS=OFF `
    -DSNAPPY_BUILD_TESTS=OFF `
    ..

cmake --build . --target install --config Release

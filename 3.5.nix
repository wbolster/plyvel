with import <nixpkgs> {}; {
  plyvel = stdenv.mkDerivation {
    name = "plyvel";
    buildInputs = with pkgs; [
      leveldb
      python35Packages.cython
      python35Packages.virtualenv
      python35Packages.pytest
      python35Packages.sphinx
    ];
    C_INCLUDE_PATH="${leveldb}/include/leveldb";
    shellHook =
    ''
      test -d .virtualenv-3.5 || virtualenv-3.5 .virtualenv-3.5
      . .virtualenv-3.5/bin/activate
    '';
  };
}

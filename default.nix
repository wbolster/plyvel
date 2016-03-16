with import <nixpkgs> {}; {
  plyvel = stdenv.mkDerivation {
    name = "plyvel";
    buildInputs = with pkgs; [
      leveldb
      python35Packages.cython
      python35Packages.virtualenv
      python35Packages.pytest
    ];
    C_INCLUDE_PATH="${leveldb}/include/leveldb";
    shellHook =
    ''
      test -d .virtualenv || virtualenv-3.5 .virtualenv
      . .virtualenv/bin/activate
    '';
  };
}

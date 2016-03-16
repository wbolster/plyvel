with import <nixpkgs> {}; {
  plyvel = stdenv.mkDerivation {
    name = "plyvel";
    buildInputs = with pkgs; [
      leveldb
      python27Packages.cython
      python27Packages.virtualenv
      python27Packages.pytest
    ];
    C_INCLUDE_PATH="${leveldb}/include/leveldb";
    shellHook =
    ''
      test -d .virtualenv-2.7 || virtualenv-2.7 .virtualenv-2.7
      . .virtualenv-2.7/bin/activate
    '';
  };
}

- If occure Bus error on nano device, run this
    - sudo mv /usr/lib/aarch64-linux-gnu/vlc/plugins/codec/libomxil_plugin.so /usr/lib/aarch64-linux-gnu/vlc/plugins/codec/libomxil_plugin.so.old


1. arm64 nodejs and npm
    - wget https://nodejs.org/dist/v16.18.0/node-v16.18.0-linux-arm64.tar.xz
    - xz -d node-v16.18.0-linux-arm64.tar.xz
    - tar xf node-v16.18.0-linux-arm64.tar
    - sudo cp -r node-v16.18.0-linux-arm64/ /usr/local
    - sudo ln -s /usr/local/node-v16.18.0-linux-arm64/bin/node /usr/local/bin/node
    - sudo ln -s /usr/local/node-v16.18.0-linux-arm64/bin/npm /usr/local/bin/npm
    - sudo ln -s /usr/local/node-v16.18.0-linux-arm64/bin/npx /usr/local/bin/npx

2. npm install --save-dev electron (按照https://zhuanlan.zhihu.com/p/37999476安裝electron)
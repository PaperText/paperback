<a name="0.1.0"></a>
## 0.1.0 PaperBack
🗄API of 📎PaperText app (2020-05-26)


#### Bug Fixes

*   :pencil: improved variable description ([ed30b3a5](https://github.com/PaperText/paperback/commit/ed30b3a58b56af76362ba89a1362cef25a07634e))
*   :pencil: separeted description to new line ([d8fad2c2](https://github.com/PaperText/paperback/commit/d8fad2c2f4db6c4149c4da6fa8cbaaf8c133861a))
*   fixed paperback cli link and added usefull urls ([1c26d3c2](https://github.com/PaperText/paperback/commit/1c26d3c285790ec03b89d1630ca536b209812b91))
*   fixed sphynx version determination ([1c7d965a](https://github.com/PaperText/paperback/commit/1c7d965a5e5a18ca5748ce69ecb4872ebbf9ac3d))
*   fix read-the-docs issue ([d5bcbe53](https://github.com/PaperText/paperback/commit/d5bcbe53f7f9039405e38580975ffc93ded9ac50))
*   fixed bug when building docs ([65114c58](https://github.com/PaperText/paperback/commit/65114c586c443b35ed4065769d74889e1d7db05e))
*   fixed output dir for docs building script ([23bd73ed](https://github.com/PaperText/paperback/commit/23bd73ed446eeebe9cbcc9aa8dcf46ded347b6e9))
*   fixed path to docs source folder in sripts ([b83a9506](https://github.com/PaperText/paperback/commit/b83a9506f69822c17c127ad732fdfe9788ea060c))
*   fixed link to paperback and removed unused dependency ([65ea4ae6](https://github.com/PaperText/paperback/commit/65ea4ae6e3918b8d976ca28a124b522a5384a35a))
*   fixed call to renamed folder/(python module) ([ddeb071c](https://github.com/PaperText/paperback/commit/ddeb071c637fbdb30e166bf26cdd35e0a7b158fe))
*   fixed import related errors ([8adc3e9d](https://github.com/PaperText/paperback/commit/8adc3e9d3565907a28c074aba3b0b00892e889b2))
*   fixed debug information ([41da1d70](https://github.com/PaperText/paperback/commit/41da1d709000ea71e0fa3c27b062c5af8cc42b64))
*   renamed inner functions and support for `-m` call ([d166f7ff](https://github.com/PaperText/paperback/commit/d166f7ff93eb2e15210fc245168911e4c83f178b))
*   removed cli form module export ([f513cf93](https://github.com/PaperText/paperback/commit/f513cf939cee7704c22cf7ab9ca5a7713192bf00))
* **Base:**  fixed type annotation for token checker function ([a737691c](https://github.com/PaperText/paperback/commit/a737691c7d7313b6dee5f00eaa5062f3e3d42dde))
* **Basetext:**   spruced up BaseText class ([704137db](https://github.com/PaperText/paperback/commit/704137db42257420b7686bdc9e3e03f623ab8ab7))
* **Exceptions:**  renamed parameter in init from name to token ([0657436e](https://github.com/PaperText/paperback/commit/0657436ea755ec975db4ffb3a630ca44472e45fb))
* **README.md:**  fixed some typos and specified Development section ([f6bc39ef](https://github.com/PaperText/paperback/commit/f6bc39eff365426a352fef6333f949c917ce31c6))
* **abc:**
  *  :recycle: changed the source of dependency ([ab3ecad8](https://github.com/PaperText/paperback/commit/ab3ecad8e518cb5f159bc06635e7b9cee98e7436))
  *  fixed wrong import in __init__ file ([3e63df1b](https://github.com/PaperText/paperback/commit/3e63df1b63fd6e31a47b31bd348daff7ffe954ba))
  *  added misc class import to pt_abc ([9f137ab4](https://github.com/PaperText/paperback/commit/9f137ab4c87ea6306aae480297bc5c5681ff5241))
* **abc.auth:**  fixed auth module declaration added docstring with new attribute and removed redundant init method ([4d604b0d](https://github.com/PaperText/paperback/commit/4d604b0d260e519f4ff089444228e7f1011be347))
* **cli:**
  *  fixed reference in cli ([ea6d8b62](https://github.com/PaperText/paperback/commit/ea6d8b62bad42e13c1d581f66b1f33ca21d94c50))
  *  fixed typo ([5cfba55b](https://github.com/PaperText/paperback/commit/5cfba55b5341cab3bef92e5da0ef24715d9101b3))
* **container:**  :ambulance: fixed line braking issue in Dockerfile ([b6e23352](https://github.com/PaperText/paperback/commit/b6e2335264c09e2efe953820102a81c81f96afb4))
* **core:**
  *  :zap: improved configuration access ([57895b0d](https://github.com/PaperText/paperback/commit/57895b0d4eced8a1540ab9884e98dbf729fc220b))
  *  :zap: very important performanci improvments ([65e7fe39](https://github.com/PaperText/paperback/commit/65e7fe391f6ac94ad21bd7289471578905b72665))
  *  :zap: very important performance fix ([c129cc70](https://github.com/PaperText/paperback/commit/c129cc707bef838fa58b962d8fedcaf7fd3b6330))
  *  :bug: fixed a bug that owerwriten config file if it existed and --create-config argument was used ([6133b83e](https://github.com/PaperText/paperback/commit/6133b83e5178a20b973159ba253d650b778c9e66))
  *  fixed exception handler status and naming ([79416c5a](https://github.com/PaperText/paperback/commit/79416c5afe12270c6f18adf2ef5a6006ea540c69))
  *  started providing keys_folder to Auth's module init ([1ea51ccf](https://github.com/PaperText/paperback/commit/1ea51ccf19adf7bb4ffdf48f56ee5094cba0ffe0))
  *  fixed name of BaseText in cores imports ([060283b4](https://github.com/PaperText/paperback/commit/060283b4298b7147f7e7a8a6fc451257cd6a0289))
  *   fixed cfg creation and moved inheritance check ([f71d746b](https://github.com/PaperText/paperback/commit/f71d746b9c09bb459ad951a2fc19bb08b68397af))
* **init:**  fixed name of BaseText ([6e4c18ff](https://github.com/PaperText/paperback/commit/6e4c18ff73e3c75901d5f77728b1d330118fc175))
* **pt_abc:**  added BaseText to import in submodule `pt_abc` ([b07a1fc7](https://github.com/PaperText/paperback/commit/b07a1fc7418d1c7cfb06c6046ce1602c5cf30527))

#### Features

*   added info and fixed some typos ([a32f0fb8](https://github.com/PaperText/paperback/commit/a32f0fb87d87ad604713800bf5ea1cddd77bdbb0))
*   added basic Dockerfile ([eccbe21b](https://github.com/PaperText/paperback/commit/eccbe21bcc7f7312552ae330282147c0507cd6fe))
*   added more info ([fc20e84d](https://github.com/PaperText/paperback/commit/fc20e84d07e47cd781914687ea6dd55f2ce8f418))
*   changed the way version is determined ([05341f9b](https://github.com/PaperText/paperback/commit/05341f9b92f76c4294ed567fdb31b8e332356d13))
*   changed the way version is determined ([7bd9b082](https://github.com/PaperText/paperback/commit/7bd9b082ba3d462bf34f261ba62f5b5a8bf9b8d1))
*   added badges ([fbc6da0d](https://github.com/PaperText/paperback/commit/fbc6da0d1535e8255daf27dea3f55ccfea172c36))
*   renamed docs_out to docs and added local poetry configuration file ([c415a10f](https://github.com/PaperText/paperback/commit/c415a10f60589701f2bfd55dbdc55862daefabc0))
*   added read-the-docks configuration file ([76c2ff0c](https://github.com/PaperText/paperback/commit/76c2ff0c82e931d21d4f77c7f6fc8321327619b9))
*   changed isort configuration ([1d08b431](https://github.com/PaperText/paperback/commit/1d08b431dfdf01c44083911f35f5421fafed4852))
*   added jetbrains IDE tasks to git files for easier collaboration ([563a2c4a](https://github.com/PaperText/paperback/commit/563a2c4a83fe355ca294771dde5273365cc1d3f7))
*   added everything from pt_abc to module scope ([92af6983](https://github.com/PaperText/paperback/commit/92af69838e245ed54200dca986d5338fbe215a2d))
* **BaseAuth:**  added method get_user_from_token and rearranged some methods and functions ([94a6d932](https://github.com/PaperText/paperback/commit/94a6d9323242fcc4523e4035bc09ad765014c5d4))
* **README:**  added note to Usage ([e71501c4](https://github.com/PaperText/paperback/commit/e71501c4ec5f3a7285a7fc32ba9e331755a553d8))
* **README.md:**  added info about Usage and Development ([8730a8be](https://github.com/PaperText/paperback/commit/8730a8be308a76275a56c1056ff936ac89c55548))
* **abc:**  :truck: moved models to abc.modles to avoid cycling import and improve readability ([4d31ba44](https://github.com/PaperText/paperback/commit/4d31ba445fa16d88d6d24f1da6a5d097c77de47f))
* **abc.Base:**
  *  simplified custom routes creation ([77354b5e](https://github.com/PaperText/paperback/commit/77354b5e5d6527908ab4e3ebf52b6ef4262ff9aa))
  *  added support for optional storage directory ([9a2b6da2](https://github.com/PaperText/paperback/commit/9a2b6da25c096079a2772aa93194ed4772918711))
* **abc.auth:**
  *  :sparkles: added ability to configure organisation ([6fdccc36](https://github.com/PaperText/paperback/commit/6fdccc36ea5b9ea3a7e0731f31797ef34abfad68))
  *  made add_CORS regular method with predefined open CORS ([c98f22be](https://github.com/PaperText/paperback/commit/c98f22be40301b504fd2d49b392602e11ab55588))
  *  improved dependency  managment and module configuration ([0fdebad5](https://github.com/PaperText/paperback/commit/0fdebad5d0578701c16eb2504eab777b12cafc68))
* **abc.docs:**  added ability to provide storage dir to docstring ([753eb222](https://github.com/PaperText/paperback/commit/753eb222e5fc3e4cf29f71512a12362788166e9a))
* **abc.misc:**  added general class added general class with ability to accept auth and docs module ([88afebea](https://github.com/PaperText/paperback/commit/88afebea69616933751a5efa594847ed9d877dd7))
* **container:**
  *  :sparkles: added argon2 as default hashing algorith ([c7ec3bd6](https://github.com/PaperText/paperback/commit/c7ec3bd63b9cb759935c1a2745e2ee55b937ca5e))
  *  :sparkles: added new feature for creating config ([3478e8b4](https://github.com/PaperText/paperback/commit/3478e8b4130a13e6c82c872a1fa29f681a460c1b))
  *  :sparkles: improved container ([359a8b1a](https://github.com/PaperText/paperback/commit/359a8b1a981c7f0b4acab22309ce73a559dde347))
* **core:**
  *  added ability to provide storage dir ([d8bdb06d](https://github.com/PaperText/paperback/commit/d8bdb06d23d4b425fde6c587815db65c591b6111))
  *  added docs with sphinx ([48790cf1](https://github.com/PaperText/paperback/commit/48790cf145b6778e0a1cd58ac2635d3c02746b09))
  *   added handler for GeneralException ([7de85950](https://github.com/PaperText/paperback/commit/7de85950aa540567fe53ed58c8f43bc5b911c4cc))
* **docs:**  :truck: renamed docs folder to `paperback_docs` to avoid confusion ([2648301a](https://github.com/PaperText/paperback/commit/2648301a320ef830bd2bf3a57ece2e2fa916d01e))
* **exceptions:**  added GeneralException ([1bfcc889](https://github.com/PaperText/paperback/commit/1bfcc889f6a9c28673f19e83f33c6eb1baf28301))
* **license:**  added MIT license ([60c612a1](https://github.com/PaperText/paperback/commit/60c612a179f02a427bf77cfb2a0e8986424dbbd7))
* **pyproject.toml:**  added fastecdsa as dependency ([c6f1c53c](https://github.com/PaperText/paperback/commit/c6f1c53c1610209354c571a260a92ea6749eed44))




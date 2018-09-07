namespace cpp proxy.security
namespace php proxy.security

struct ResultStruct {
  1: i32    err,
  2: string msg,
  3: string str
}

struct ResultListWithFlag {
  1: string flag,
  2: map<string, ResultStruct> BatchResultStruct
}

service SecurityService {
  // 不带 UseEcbModel 后缀的，接口默认使用CBC算法模式
  ResultStruct encrypt(1: string str),
  ResultStruct decrypt(1: string str),
  map<string, ResultStruct> batchEncrypt(1: map<string, string> vec),
  map<string, ResultStruct> batchDecrypt(1: map<string, string> vec),
  ResultListWithFlag batchEncryptWithFlag(1: string flag, 2: map<string, string> vec),
  ResultListWithFlag batchDecryptWithFlag(1: string flag, 2: map<string, string> vec),

  ResultStruct encryptAndBase64(1: string str),
  ResultStruct decryptAndBase64(1: string str),
  map<string, ResultStruct> batchEncryptAndBase64(1: map<string, string> vec),
  map<string, ResultStruct> batchDecryptAndBase64(1: map<string, string> vec),
  ResultListWithFlag batchEncryptWithFlagAndBase64(1: string flag, 2: map<string, string> vec),
  ResultListWithFlag batchDecryptWithFlagAndBase64(1: string flag, 2: map<string, string> vec),

  // 使用ECB算法模式加解密，同样的明文得到的密文跟默认用CBC模式的密文不一样
  ResultStruct encryptUseEcbModel(1: string str),
  ResultStruct decryptUseEcbModel(1: string str),
  map<string, ResultStruct> batchEncryptUseEcbModel(1: map<string, string> vec),
  map<string, ResultStruct> batchDecryptUseEcbModel(1: map<string, string> vec)
}

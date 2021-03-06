#pragma once
#include <string>

namespace Map2Check {
// TODO(rafa.sa.xp@gmail.com): make logging levels
class Log {
private:
  static bool isDebugMode;  
 public:
  static void ActivateDebugMode() { isDebugMode = true;}
  static void Error(std::string msg);
  static void Warning(std::string msg);
  static void Debug(std::string msg);
  static void Info(std::string msg);
  static void Fatal(std::string msg);
};

}  // namespace Map2Check

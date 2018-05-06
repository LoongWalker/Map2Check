#pragma once

#include <stdint.h>
#include <string>
#include <memory>

namespace Map2Check {

class AFL_COMPILE {
 private:
  /** Current afl_clang command (with path) */
  std::string afl_clang;
 public:
  /** Default constructor */
  AFL_COMPILE() {}
  /**
   * Return afl-clang command
   * @return Returns a string with afl-clang command
  */
  std::string getCommand();
  /**
   * Set path for current afl-clang binary folder
   * @param  String with path
  */
  void setPath(std::string path);
};

class AFL_EXEC {
 private:
  /** Current afl_fuzz command (with path) */
  std::string afl_fuzz;
  /** Timeout for AFL execution */
  u_int32_t timeout;
  /** Stop on crash */
  bool benchUntilCrash;
  /** Skip AFL verification */
  bool skipCpuFreq;

 public:
  AFL_EXEC() {}
  void setPath(std::string path);
  void setTimeout(u_int32_t timeout);
  void setBenchUntilCrash(bool isOn);
  void setSkipCpuFreq(bool isOn);
  std::string getCommand();
};

class AFL {
 protected:
  std::unique_ptr<AFL_EXEC> executor;
  std::unique_ptr<AFL_COMPILE> compiler;
 public:
  explicit AFL(std::string path) {
    this->compiler = std::make_unique<AFL_COMPILE>();
    this->compiler->setPath(path);

    this->executor = std::make_unique<AFL_EXEC>();
    this->executor->setPath(path);
  }
  std::string getCompilerCommand() {
    return compiler->getCommand();
  }
  std::string getExecutionCommand() {
    return executor->getCommand();
  }
};

class AFL_MAP2CHECK : public AFL {
 public:
  AFL_MAP2CHECK() : AFL("custom_path/") {
    this->executor->setBenchUntilCrash(true);
    this->executor->setSkipCpuFreq(true);
    this->executor->setTimeout(180);
  }
};
}  // namespace Map2Check

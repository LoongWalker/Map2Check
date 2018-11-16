#pragma once

#include <llvm/IR/Constants.h>
#include <llvm/IR/Function.h>
#include <llvm/IR/IRBuilder.h>
#include <llvm/IR/Instructions.h>
#include <llvm/IR/Metadata.h>
#include <llvm/IR/Module.h>
#include <llvm/Pass.h>
#include <llvm/Support/raw_ostream.h>

#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include <memory>

#include "../../frontend/utils/tools.hpp"
#include "DebugInfo.hpp"
#include "LibraryFunctions.hpp"

using namespace llvm;
namespace Tools = Map2Check;

struct ForcePredAsAssumePass : public FunctionPass {
  static char ID;
  ForcePredAsAssumePass() : FunctionPass(ID) {}
  ForcePredAsAssumePass(std::string c_program_path) : FunctionPass(ID) {
    this->c_program_path = c_program_path;
    this->sourceCodeHelper = make_unique<Tools::SourceCodeHelper>(
        Tools::SourceCodeHelper(c_program_path));
  }
  virtual bool runOnFunction(Function& F);

 protected:
  void runOnBasicBlock(BasicBlock& B, LLVMContext* Ctx);   

 private:
  std::unique_ptr<Tools::SourceCodeHelper> sourceCodeHelper;
  std::string c_program_path;
  std::unique_ptr<LibraryFunctions> libraryFunctions;  
  Function* currentFunction;
  LLVMContext* Ctx;  
};

class ForcePredAsAssumePassException : public std::runtime_error {
 public:
  ForcePredAsAssumePassException(std::string message)
      : std::runtime_error(message) {}
  virtual const char* what() const throw();
};

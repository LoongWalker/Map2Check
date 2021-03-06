#pragma once
#include "edge.hpp"
#include "node.hpp"
#include "witness.hpp"

using namespace Map2Check;
namespace Map2Check {
class Graph {
 protected:
  std::string id;
  std::vector<std::unique_ptr<DataElement>> elements;
  std::vector<std::unique_ptr<Node>> states;
  std::vector<std::unique_ptr<Edge>> transitions;
  virtual std::string convertToString();

 public:
  Graph() {}
  virtual void AddElement(std::unique_ptr<DataElement> element);
  virtual void AddNode(std::unique_ptr<Node> node);
  virtual void AddEdge(std::unique_ptr<Edge> edge);
  operator std::string() { return this->convertToString(); }
};

class ViolationWitnessGraph : public Graph {
 protected:
  virtual std::string convertToString();

 public:
  ViolationWitnessGraph() : Graph() {}
};

class CorrectnessWitnessGraph : public Graph {
 protected:
  virtual std::string convertToString();

 public:
  CorrectnessWitnessGraph() : Graph() {}
};

class SVCompWitness {
 protected:
  std::unique_ptr<Graph> automata;
  std::string programHash;
  void makeViolationAutomata();
  void makeCorrectnessSVComp();
  void makeCorrectnessAutomata();
  void makeViolationAutomataAux();  // when we don't have KLEE values
 public:
  SVCompWitness(std::string programPath, std::string programHash,
                std::string targetFunction = "",
                std::string specTrueString = "");
  void Testify();
};
}  // namespace Map2Check

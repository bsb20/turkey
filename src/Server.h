#pragma once
#include "Common.h"
#include "ProcReader.h"

namespace Turkey {
class Server {
public:
  Server();
  ~Server();

  Server(const Server&) = delete;
  Server& operator=(const Server&) = delete;

  void poll();

private:
  ProcReader procReader_;
};
}

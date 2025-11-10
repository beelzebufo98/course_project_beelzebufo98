import http from "k6/http";
import { sleep, check } from "k6";
import { Counter } from "k6/metrics";
const failedRequests = new Counter("failed_requests");

export const options = {
  stages: [
    { duration: "30s", target: 30 },
    { duration: "2m", target: 30 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<200"],
    failed_requests: ["count<1"],
  },
};

export default function () {
  const res = http.get("http://localhost:8000/wishes/1");
  if (res.status >= 500 || (res.status >= 400 && res.status !== 429)) {
    failedRequests.add(1);
  }
}

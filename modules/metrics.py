from aioprometheus.collectors import Counter


class Metrics:
    database_failures = Counter("database_failures", "Number of failed database w/r attempts")
    auth_failures = Counter("auth_failures", "Number of failed auth attempts")
    timeout_failures = Counter("timeout_failures", "Number of timeout failures")
    security_failures = Counter("security_failures", "Number of forbidden action failures")
    unhandled_failures = Counter("unhandled_failures", "Number of unhandled failures")
    connection_failures = Counter("connection_failures", "Number of connection related failures")

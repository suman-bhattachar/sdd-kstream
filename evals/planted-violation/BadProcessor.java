// Fixture: deliberate §7 violation — synchronous DB access inside a processor.
class BadProcessor implements Processor<String, String, String, String> {
    private final JdbcTemplate jdbc; // forbidden in topology
    public void process(Record<String, String> r) {
        var row = jdbc.queryForObject("select 1", Integer.class); // blocking I/O on the stream thread
    }
}

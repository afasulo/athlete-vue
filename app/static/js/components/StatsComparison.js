const StatsComparison = () => {
  const [primaryInterval, setPrimaryInterval] = useState('7');
  const [comparisonInterval, setComparisonInterval] = useState('');
  const [stats, setStats] = useState(null);

  const intervals = {
    '7': 'Last 7 Days',
    '14': 'Last 14 Days',
    '30': 'Last 30 Days',
    '90': 'Last 90 Days',
    '180': 'Last 6 Months',
    '365': 'Last 12 Months'
  };

  useEffect(() => {
    const fetchStats = async () => {
      let url = `/api/player/${userId}/interval-stats?interval=${primaryInterval}`;
      if (comparisonInterval) {
        url += `&compare_to=${comparisonInterval}`;
      }
      const response = await fetch(url);
      const data = await response.json();
      setStats(data);
    };
    fetchStats();
  }, [primaryInterval, comparisonInterval]);

  return (
    <div className="card">
      <div className="card-body">
        <div className="row mb-4">
          <div className="col-md-6">
            <label className="form-label">Select Time Period</label>
            <select 
              className="form-select"
              value={primaryInterval}
              onChange={(e) => setPrimaryInterval(e.target.value)}
            >
              {Object.entries(intervals).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
          <div className="col-md-6">
            <label className="form-label">Compare With (Optional)</label>
            <select 
              className="form-select"
              value={comparisonInterval}
              onChange={(e) => setComparisonInterval(e.target.value)}
            >
              <option value="">No Comparison</option>
              {Object.entries(intervals).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
          </div>
        </div>

        {stats?.primary_stats && (
          <div className="row">
            <div className="col-12">
              <table className="table">
                <thead>
                  <tr>
                    <th>Metric</th>
                    <th>{intervals[primaryInterval]}</th>
                    {stats.comparison_stats && (
                      <>
                        <th>{intervals[comparisonInterval]}</th>
                        <th>Change</th>
                      </>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {[
                    ['Total Hits', 'total_hits'],
                    ['Avg Exit Velo', 'avg_exit_velo', ' mph'],
                    ['Max Exit Velo', 'max_exit_velo', ' mph'],
                    ['Avg Distance', 'avg_distance', ' ft'],
                    ['Max Distance', 'max_distance', ' ft'],
                    ['Singles', 'singles'],
                    ['Doubles', 'doubles'],
                    ['Triples', 'triples'],
                    ['Home Runs', 'home_runs'],
                    ['Batting Avg', 'batting_avg']
                  ].map(([label, key, unit = '']) => (
                    <tr key={key}>
                      <td>{label}</td>
                      <td>{stats.primary_stats[key]}{unit}</td>
                      {stats.comparison_stats && (
                        <>
                          <td>{stats.comparison_stats[key]}{unit}</td>
                          <td className={`${stats.improvements?.[key] > 0 ? 'text-success' : 'text-danger'}`}>
                            {stats.improvements?.[key] > 0 ? '+' : ''}
                            {stats.improvements?.[key]}{unit}
                          </td>
                        </>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StatsComparison;
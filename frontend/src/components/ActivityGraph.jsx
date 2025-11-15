import { useState } from "react";

const activityData = [
  { month: "Aug", matched: 18, applied: 8, interviews: 2, offers: 0 },
  { month: "Sep", matched: 24, applied: 11, interviews: 3, offers: 1 },
  { month: "Oct", matched: 32, applied: 16, interviews: 4, offers: 1 },
  { month: "Nov", matched: 40, applied: 20, interviews: 6, offers: 2 }
];

const metrics = [
  { key: "matched", label: "Matched", color: "#38bdf8" },
  { key: "applied", label: "Applied", color: "#22c55e" },
  { key: "interviews", label: "Interviews", color: "#eab308" },
  { key: "offers", label: "Offers", color: "#a855f7" }
];

export default function ActivityGraph() {
  const [hoveredPoint, setHoveredPoint] = useState(null);

  const maxValue = Math.max(
    ...activityData.flatMap((m) => [m.matched, m.applied, m.interviews, m.offers])
  );

  const chartHeight = 180;
  const chartWidth = 600;
  const padding = { top: 20, right: 20, bottom: 30, left: 40 };
  const plotHeight = chartHeight - padding.top - padding.bottom;
  const plotWidth = chartWidth - padding.left - padding.right;

  const getX = (index) => padding.left + (index * plotWidth) / (activityData.length - 1);
  const getY = (value) => padding.top + plotHeight - (value / maxValue) * plotHeight;

  const createPath = (metricKey) => {
    return activityData
      .map((d, i) => {
        const x = getX(i);
        const y = getY(d[metricKey]);
        return `${i === 0 ? "M" : "L"} ${x} ${y}`;
      })
      .join(" ");
  };

  return (
    <section style={styles.section}>
      <div style={styles.card}>
        <div style={styles.header}>
          <div>
            <h3 style={styles.title}>Monthly Activity</h3>
            <p style={styles.subtitle}>
              Matched jobs, applications, interviews and offers over time.
            </p>
          </div>
          <div style={styles.legend}>
            {metrics.map((metric) => (
              <span key={metric.key} style={styles.legendItem}>
                <span
                  style={{
                    ...styles.legendDot,
                    backgroundColor: metric.color
                  }}
                />
                {metric.label}
              </span>
            ))}
          </div>
        </div>

        <div style={styles.chartContainer}>
          <svg
            width="100%"
            height={chartHeight}
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            style={styles.svg}
          >
            {/* Y-axis grid lines */}
            {[0, 0.25, 0.5, 0.75, 1].map((ratio) => {
              const y = padding.top + plotHeight * (1 - ratio);
              return (
                <g key={ratio}>
                  <line
                    x1={padding.left}
                    y1={y}
                    x2={chartWidth - padding.right}
                    y2={y}
                    stroke="rgba(148, 163, 184, 0.15)"
                    strokeWidth="1"
                  />
                  <text
                    x={padding.left - 8}
                    y={y + 4}
                    fill="#9ca3af"
                    fontSize="11"
                    textAnchor="end"
                  >
                    {Math.round(maxValue * ratio)}
                  </text>
                </g>
              );
            })}

            {/* Draw lines */}
            {metrics.map((metric) => (
              <path
                key={metric.key}
                d={createPath(metric.key)}
                fill="none"
                stroke={metric.color}
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            ))}

            {/* Draw dots and invisible hover areas */}
            {metrics.map((metric) =>
              activityData.map((d, i) => {
                const x = getX(i);
                const y = getY(d[metric.key]);
                const pointId = `${metric.key}-${i}`;
                const isHovered = hoveredPoint === pointId;

                return (
                  <g key={pointId}>
                    {/* Invisible larger circle for easier hovering */}
                    <circle
                      cx={x}
                      cy={y}
                      r="12"
                      fill="transparent"
                      style={{ cursor: "pointer" }}
                      onMouseEnter={() => setHoveredPoint(pointId)}
                      onMouseLeave={() => setHoveredPoint(null)}
                    />
                    {/* Visible dot */}
                    <circle
                      cx={x}
                      cy={y}
                      r={isHovered ? "6" : "4"}
                      fill={metric.color}
                      stroke="rgba(15, 23, 42, 0.96)"
                      strokeWidth="2"
                      style={{
                        transition: "r 0.2s ease",
                        cursor: "pointer"
                      }}
                    />
                    {/* Tooltip on hover */}
                    {isHovered && (
                      <g>
                        <rect
                          x={x - 35}
                          y={y - 40}
                          width="70"
                          height="30"
                          rx="6"
                          fill="rgba(15, 23, 42, 0.98)"
                          stroke={metric.color}
                          strokeWidth="1.5"
                        />
                        <text
                          x={x}
                          y={y - 28}
                          fill="#fff"
                          fontSize="11"
                          fontWeight="600"
                          textAnchor="middle"
                        >
                          {metric.label}
                        </text>
                        <text
                          x={x}
                          y={y - 16}
                          fill={metric.color}
                          fontSize="13"
                          fontWeight="700"
                          textAnchor="middle"
                        >
                          {d[metric.key]}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })
            )}

            {/* X-axis labels */}
            {activityData.map((d, i) => {
              const x = getX(i);
              return (
                <text
                  key={d.month}
                  x={x}
                  y={chartHeight - 8}
                  fill="#9ca3af"
                  fontSize="12"
                  textAnchor="middle"
                >
                  {d.month}
                </text>
              );
            })}
          </svg>
        </div>
      </div>
    </section>
  );
}

const styles = {
  section: {
    marginTop: "12px",
    marginBottom: "24px"
  },
  card: {
    borderRadius: "20px",
    background: "rgba(15, 23, 42, 0.96)",
    border: "1px solid rgba(148, 163, 184, 0.45)",
    padding: "14px 18px"
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "12px",
    marginBottom: "10px",
    flexWrap: "wrap"
  },
  title: {
    margin: 0,
    fontSize: "0.95rem",
    color: "#fff"
  },
  subtitle: {
    margin: "2px 0 0 0",
    fontSize: "0.78rem",
    color: "#9ca3af"
  },
  legend: {
    display: "flex",
    flexWrap: "wrap",
    gap: "12px",
    fontSize: "0.72rem",
    color: "#9ca3af"
  },
  legendItem: {
    display: "flex",
    alignItems: "center",
    gap: "4px"
  },
  legendDot: {
    width: "9px",
    height: "9px",
    borderRadius: "999px",
    display: "inline-block"
  },
  chartContainer: {
    paddingTop: "6px",
    overflow: "visible"
  },
  svg: {
    overflow: "visible"
  }
};
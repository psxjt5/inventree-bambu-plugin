import React, { useEffect, useState } from "react";
import { Card } from "@mantine/core";

export default function BambuDashboardWidget({ machine }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`/api/plugin/inventreebambuplugin/machine/${machine.pk}/`)
      .then((res) => res.json())
      .then(setData);
  }, [machine]);

  if (!data) {
    return <Card>Loading...</Card>;
  }

  return (
    <Card shadow="sm" padding="lg">
      <h3>{machine.name}</h3>

      <p><strong>Status:</strong> {data.state}</p>
      <p><strong>Progress:</strong> {data.progress}%</p>
      <p><strong>Bed:</strong> {data.bed_temp}°C</p>
      <p><strong>Nozzle:</strong> {data.nozzle_temp}°C</p>
      <p><strong>Job:</strong> {data.job_name}</p>
      <p><strong>Remaining:</strong> {data.remaining_time}s</p>
    </Card>
  );
}
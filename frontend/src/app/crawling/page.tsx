"use client";

import { useState, useEffect } from "react";
import {
  RefreshCw,
  Play,
  Square,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Calendar,
  Settings,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Select, MultiSelect } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Table,
  TableHeader,
  TableBody,
  TableHead,
  TableRow,
  TableCell,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Spinner, TableSkeleton } from "@/components/ui/loading";
import { useCompanies } from "@/hooks/useCompanies";
import {
  useCrawlingStatus,
  useCrawlingSchedule,
  useCrawlLogs,
  useStartCrawling,
  useStopCrawling,
  useUpdateSchedule,
} from "@/hooks/useCrawling";

export default function CrawlingPage() {
  const [activeTab, setActiveTab] = useState("status");
  const [selectedCompanies, setSelectedCompanies] = useState<string[]>([]);
  const [logPage, setLogPage] = useState(1);
  const [logFilter, setLogFilter] = useState<string>("");

  // Fetch data
  const [isPolling, setIsPolling] = useState(false);
  const { data: companiesData } = useCompanies({ page_size: 100, is_active: true });
  const { data: status, isLoading: statusLoading } = useCrawlingStatus(
    isPolling ? 3000 : undefined
  );

  // Update polling based on status
  useEffect(() => {
    setIsPolling(status?.is_running ?? false);
  }, [status?.is_running]);
  const { data: schedule, isLoading: scheduleLoading } = useCrawlingSchedule();
  const { data: logsData, isLoading: logsLoading } = useCrawlLogs({
    page: logPage,
    page_size: 20,
    status: logFilter || undefined,
  });

  // Mutations
  const startMutation = useStartCrawling();
  const stopMutation = useStopCrawling();
  const updateScheduleMutation = useUpdateSchedule();

  // Schedule form state
  const [scheduleForm, setScheduleForm] = useState({
    enabled: false,
    day_of_week: 0,
    hour: 3,
    minute: 0,
    timezone: "Asia/Tokyo",
  });

  useEffect(() => {
    if (schedule) {
      setScheduleForm({
        enabled: schedule.enabled,
        day_of_week: schedule.day_of_week,
        hour: schedule.hour,
        minute: schedule.minute,
        timezone: schedule.timezone,
      });
    }
  }, [schedule]);

  const companyOptions =
    companiesData?.items.map((c) => ({
      value: c.id.toString(),
      label: c.name_en,
    })) || [];

  const handleStartCrawl = async () => {
    const companyIds =
      selectedCompanies.length > 0
        ? selectedCompanies.map((id) => parseInt(id))
        : undefined;
    await startMutation.mutateAsync({ companyIds });
  };

  const handleStopCrawl = async () => {
    await stopMutation.mutateAsync();
  };

  const handleSaveSchedule = async () => {
    await updateScheduleMutation.mutateAsync(scheduleForm);
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "-";
    return new Date(dateString).toLocaleString("ja-JP");
  };

  const formatDuration = (seconds: number | null) => {
    if (seconds === null) return "-";
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const getStatusIcon = (logStatus: string) => {
    switch (logStatus) {
      case "success":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-destructive" />;
      case "running":
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case "partial":
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadge = (logStatus: string) => {
    switch (logStatus) {
      case "success":
        return <Badge className="bg-green-500">Success</Badge>;
      case "failed":
        return <Badge variant="destructive">Failed</Badge>;
      case "running":
        return <Badge className="bg-blue-500">Running</Badge>;
      case "partial":
        return <Badge className="bg-yellow-500">Partial</Badge>;
      default:
        return <Badge variant="secondary">{logStatus}</Badge>;
    }
  };

  const dayOptions = [
    { value: "0", label: "Monday" },
    { value: "1", label: "Tuesday" },
    { value: "2", label: "Wednesday" },
    { value: "3", label: "Thursday" },
    { value: "4", label: "Friday" },
    { value: "5", label: "Saturday" },
    { value: "6", label: "Sunday" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <RefreshCw className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Crawling Management</h1>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="status">Status & Control</TabsTrigger>
          <TabsTrigger value="schedule">Schedule</TabsTrigger>
          <TabsTrigger value="logs">Logs</TabsTrigger>
        </TabsList>

        {/* Status & Control Tab */}
        <TabsContent value="status">
          <div className="grid gap-6">
            {/* Current Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {status?.is_running ? (
                    <RefreshCw className="h-5 w-5 animate-spin text-blue-500" />
                  ) : (
                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                  )}
                  Crawling Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                {statusLoading ? (
                  <Spinner />
                ) : (
                  <div className="grid gap-4 md:grid-cols-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Status</p>
                      <p className="text-lg font-medium">
                        {status?.is_running ? (
                          <Badge className="bg-blue-500">Running</Badge>
                        ) : (
                          <Badge variant="secondary">Idle</Badge>
                        )}
                      </p>
                    </div>
                    {status?.is_running && status.current_company && (
                      <div>
                        <p className="text-sm text-muted-foreground">Current Company</p>
                        <p className="text-lg font-medium">{status.current_company}</p>
                      </div>
                    )}
                    {status?.is_running && status.progress !== undefined && (
                      <div>
                        <p className="text-sm text-muted-foreground">Progress</p>
                        <div className="flex items-center gap-2">
                          <div className="w-full bg-muted rounded-full h-2">
                            <div
                              className="bg-primary h-2 rounded-full transition-all"
                              style={{ width: `${status.progress}%` }}
                            />
                          </div>
                          <span className="text-sm">{status.progress}%</span>
                        </div>
                      </div>
                    )}
                    <div>
                      <p className="text-sm text-muted-foreground">Last Crawl</p>
                      <p className="text-sm">{formatDate(status?.last_crawl_at || null)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Next Scheduled</p>
                      <p className="text-sm">{formatDate(status?.next_scheduled_at || null)}</p>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Manual Crawl */}
            <Card>
              <CardHeader>
                <CardTitle>Manual Crawl</CardTitle>
                <CardDescription>
                  Start a manual crawl for all or selected companies.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <MultiSelect
                  options={companyOptions}
                  value={selectedCompanies}
                  onChange={setSelectedCompanies}
                  label="Select Companies (leave empty for all)"
                  placeholder="All active companies"
                />

                <div className="flex gap-2">
                  {status?.is_running ? (
                    <Button
                      variant="destructive"
                      onClick={handleStopCrawl}
                      disabled={stopMutation.isPending}
                    >
                      <Square className="h-4 w-4 mr-2" />
                      {stopMutation.isPending ? "Stopping..." : "Stop Crawl"}
                    </Button>
                  ) : (
                    <Button onClick={handleStartCrawl} disabled={startMutation.isPending}>
                      <Play className="h-4 w-4 mr-2" />
                      {startMutation.isPending ? "Starting..." : "Start Crawl"}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Schedule Tab */}
        <TabsContent value="schedule">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Schedule Configuration
              </CardTitle>
              <CardDescription>
                Configure automatic weekly crawling schedule.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {scheduleLoading ? (
                <Spinner />
              ) : (
                <>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={scheduleForm.enabled}
                        onChange={(e) =>
                          setScheduleForm({ ...scheduleForm, enabled: e.target.checked })
                        }
                        className="h-4 w-4"
                      />
                      <span className="font-medium">Enable Scheduled Crawling</span>
                    </label>
                  </div>

                  <div className="grid gap-4 md:grid-cols-3">
                    <Select
                      options={dayOptions}
                      value={scheduleForm.day_of_week.toString()}
                      onChange={(value) =>
                        setScheduleForm({ ...scheduleForm, day_of_week: parseInt(value) })
                      }
                      label="Day of Week"
                      disabled={!scheduleForm.enabled}
                    />

                    <Input
                      type="number"
                      label="Hour (0-23)"
                      value={scheduleForm.hour}
                      onChange={(e) =>
                        setScheduleForm({ ...scheduleForm, hour: parseInt(e.target.value) || 0 })
                      }
                      min={0}
                      max={23}
                      disabled={!scheduleForm.enabled}
                    />

                    <Input
                      type="number"
                      label="Minute (0-59)"
                      value={scheduleForm.minute}
                      onChange={(e) =>
                        setScheduleForm({
                          ...scheduleForm,
                          minute: parseInt(e.target.value) || 0,
                        })
                      }
                      min={0}
                      max={59}
                      disabled={!scheduleForm.enabled}
                    />
                  </div>

                  <div className="p-4 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      Crawling will run every{" "}
                      <strong>{dayOptions[scheduleForm.day_of_week]?.label}</strong> at{" "}
                      <strong>
                        {scheduleForm.hour.toString().padStart(2, "0")}:
                        {scheduleForm.minute.toString().padStart(2, "0")}
                      </strong>{" "}
                      ({scheduleForm.timezone})
                    </p>
                  </div>

                  <Button
                    onClick={handleSaveSchedule}
                    disabled={updateScheduleMutation.isPending}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    {updateScheduleMutation.isPending ? "Saving..." : "Save Schedule"}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Logs Tab */}
        <TabsContent value="logs">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Crawl Logs</CardTitle>
                <Select
                  options={[
                    { value: "", label: "All Status" },
                    { value: "success", label: "Success" },
                    { value: "failed", label: "Failed" },
                    { value: "running", label: "Running" },
                    { value: "partial", label: "Partial" },
                  ]}
                  value={logFilter}
                  onChange={(value) => {
                    setLogFilter(value);
                    setLogPage(1);
                  }}
                  className="w-36"
                />
              </div>
            </CardHeader>
            <CardContent>
              {logsLoading ? (
                <TableSkeleton rows={10} columns={7} />
              ) : !logsData?.items.length ? (
                <div className="text-center py-8 text-muted-foreground">
                  No crawl logs found.
                </div>
              ) : (
                <>
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Status</TableHead>
                        <TableHead>Company</TableHead>
                        <TableHead>Trigger</TableHead>
                        <TableHead>Started</TableHead>
                        <TableHead>Duration</TableHead>
                        <TableHead className="text-right">Plans</TableHead>
                        <TableHead>Error</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {logsData.items.map((log) => (
                        <TableRow key={log.id}>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getStatusIcon(log.status)}
                              {getStatusBadge(log.status)}
                            </div>
                          </TableCell>
                          <TableCell>{log.company_name || "All"}</TableCell>
                          <TableCell>
                            <Badge variant="outline">{log.trigger_type}</Badge>
                          </TableCell>
                          <TableCell className="text-sm">
                            {formatDate(log.started_at)}
                          </TableCell>
                          <TableCell>{formatDuration(log.duration_seconds)}</TableCell>
                          <TableCell className="text-right">
                            <div className="text-sm">
                              <span className="text-muted-foreground">Found:</span> {log.plans_found}
                              <br />
                              <span className="text-muted-foreground">New:</span> {log.plans_created}
                              <br />
                              <span className="text-muted-foreground">Updated:</span>{" "}
                              {log.plans_updated}
                            </div>
                          </TableCell>
                          <TableCell>
                            {log.error_message ? (
                              <span
                                className="text-sm text-destructive truncate block max-w-xs"
                                title={log.error_message}
                              >
                                {log.error_message}
                              </span>
                            ) : (
                              "-"
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>

                  {/* Pagination */}
                  {logsData.total > logsData.page_size && (
                    <div className="flex items-center justify-center gap-2 mt-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setLogPage((p) => Math.max(1, p - 1))}
                        disabled={logPage === 1}
                      >
                        Previous
                      </Button>
                      <span className="text-sm text-muted-foreground">
                        Page {logPage} of {Math.ceil(logsData.total / logsData.page_size)}
                      </span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setLogPage((p) => p + 1)}
                        disabled={logPage >= Math.ceil(logsData.total / logsData.page_size)}
                      >
                        Next
                      </Button>
                    </div>
                  )}
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

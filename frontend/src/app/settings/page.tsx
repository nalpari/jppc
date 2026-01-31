"use client";

import { useState } from "react";
import {
  Settings,
  Bell,
  Mail,
  Plus,
  Trash2,
  AlertTriangle,
  TrendingUp,
  FileText,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Modal, ModalFooter } from "@/components/ui/modal";
import { Spinner } from "@/components/ui/loading";
import { useAlerts, useUpdateAlert, useAddRecipient, useRemoveRecipient } from "@/hooks/useAlerts";

export default function SettingsPage() {
  const [addRecipientModal, setAddRecipientModal] = useState<{
    isOpen: boolean;
    alertType: string;
  }>({ isOpen: false, alertType: "" });
  const [newEmail, setNewEmail] = useState("");
  const [newName, setNewName] = useState("");

  const { data: alerts, isLoading } = useAlerts();
  const updateMutation = useUpdateAlert();
  const addRecipientMutation = useAddRecipient();
  const removeRecipientMutation = useRemoveRecipient();

  const getAlertIcon = (alertType: string) => {
    switch (alertType) {
      case "crawl_failure":
        return <AlertTriangle className="h-5 w-5 text-destructive" />;
      case "price_change":
        return <TrendingUp className="h-5 w-5 text-blue-500" />;
      case "weekly_report":
        return <FileText className="h-5 w-5 text-green-500" />;
      default:
        return <Bell className="h-5 w-5" />;
    }
  };

  const getAlertTitle = (alertType: string) => {
    switch (alertType) {
      case "crawl_failure":
        return "Crawl Failure Alerts";
      case "price_change":
        return "Price Change Alerts";
      case "weekly_report":
        return "Weekly Report";
      default:
        return alertType;
    }
  };

  const getAlertDescription = (alertType: string) => {
    switch (alertType) {
      case "crawl_failure":
        return "Receive notifications when a crawl operation fails.";
      case "price_change":
        return "Get notified when electricity prices change.";
      case "weekly_report":
        return "Receive a weekly summary report of all price data.";
      default:
        return "";
    }
  };

  const handleToggleAlert = async (alertType: string, isEnabled: boolean) => {
    await updateMutation.mutateAsync({ alertType, isEnabled: !isEnabled });
  };

  const handleAddRecipient = async () => {
    if (!newEmail.trim() || !addRecipientModal.alertType) return;

    await addRecipientMutation.mutateAsync({
      alertType: addRecipientModal.alertType,
      email: newEmail.trim(),
      name: newName.trim() || undefined,
    });

    setNewEmail("");
    setNewName("");
    setAddRecipientModal({ isOpen: false, alertType: "" });
  };

  const handleRemoveRecipient = async (alertType: string, recipientId: number) => {
    await removeRecipientMutation.mutateAsync({ alertType, recipientId });
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center gap-2">
          <Settings className="h-6 w-6" />
          <h1 className="text-2xl font-bold">Settings</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <Spinner size="lg" />
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Settings className="h-6 w-6" />
        <h1 className="text-2xl font-bold">Settings</h1>
      </div>

      {/* Alert Settings */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Bell className="h-5 w-5" />
          Email Notifications
        </h2>

        {alerts?.map((alert) => (
          <Card key={alert.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  {getAlertIcon(alert.alert_type)}
                  <div>
                    <CardTitle className="text-base">
                      {getAlertTitle(alert.alert_type)}
                    </CardTitle>
                    <CardDescription>
                      {getAlertDescription(alert.alert_type)}
                    </CardDescription>
                  </div>
                </div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={alert.is_enabled}
                    onChange={() => handleToggleAlert(alert.alert_type, alert.is_enabled)}
                    className="h-4 w-4"
                    disabled={updateMutation.isPending}
                  />
                  <Badge variant={alert.is_enabled ? "default" : "secondary"}>
                    {alert.is_enabled ? "Enabled" : "Disabled"}
                  </Badge>
                </label>
              </div>
            </CardHeader>

            <CardContent className="space-y-4">
              {/* Recipients List */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Recipients</span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() =>
                      setAddRecipientModal({ isOpen: true, alertType: alert.alert_type })
                    }
                    disabled={!alert.is_enabled}
                  >
                    <Plus className="h-4 w-4 mr-1" />
                    Add
                  </Button>
                </div>

                {alert.recipients.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-2">
                    No recipients configured.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {alert.recipients.map((recipient) => (
                      <div
                        key={recipient.id}
                        className="flex items-center justify-between p-2 border rounded-lg"
                      >
                        <div className="flex items-center gap-2">
                          <Mail className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <span className="font-medium">{recipient.email}</span>
                            {recipient.name && (
                              <span className="text-sm text-muted-foreground ml-2">
                                ({recipient.name})
                              </span>
                            )}
                          </div>
                          <Badge variant={recipient.is_active ? "default" : "secondary"}>
                            {recipient.is_active ? "Active" : "Inactive"}
                          </Badge>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() =>
                            handleRemoveRecipient(alert.alert_type, recipient.id)
                          }
                          disabled={removeRecipientMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* System Settings */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Settings className="h-5 w-5" />
          System Settings
        </h2>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Timezone</CardTitle>
            <CardDescription>
              All scheduled operations use this timezone.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Asia/Tokyo (JST)</Badge>
              <span className="text-sm text-muted-foreground">
                UTC+9 - Japan Standard Time
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Data Retention</CardTitle>
            <CardDescription>
              How long historical data is kept in the system.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-2 md:grid-cols-2">
              <div className="flex items-center justify-between p-2 border rounded-lg">
                <span className="text-sm">Crawl Logs</span>
                <Badge variant="outline">90 days</Badge>
              </div>
              <div className="flex items-center justify-between p-2 border rounded-lg">
                <span className="text-sm">Price History</span>
                <Badge variant="outline">Unlimited</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">API Information</CardTitle>
            <CardDescription>
              Backend API connection details.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">API URL:</span>
                <code className="px-2 py-1 bg-muted rounded">
                  {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                </code>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">Version:</span>
                <Badge variant="outline">v1</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Add Recipient Modal */}
      <Modal
        isOpen={addRecipientModal.isOpen}
        onClose={() => setAddRecipientModal({ isOpen: false, alertType: "" })}
        title="Add Recipient"
        description="Add a new email recipient for this alert."
      >
        <div className="space-y-4">
          <Input
            label="Email Address"
            type="email"
            value={newEmail}
            onChange={(e) => setNewEmail(e.target.value)}
            placeholder="recipient@example.com"
          />
          <Input
            label="Name (optional)"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="John Doe"
          />
        </div>

        <ModalFooter>
          <Button
            variant="outline"
            onClick={() => setAddRecipientModal({ isOpen: false, alertType: "" })}
          >
            Cancel
          </Button>
          <Button
            onClick={handleAddRecipient}
            disabled={!newEmail.trim() || addRecipientMutation.isPending}
          >
            {addRecipientMutation.isPending ? "Adding..." : "Add Recipient"}
          </Button>
        </ModalFooter>
      </Modal>
    </div>
  );
}

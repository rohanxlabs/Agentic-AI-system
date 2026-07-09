"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { User, Edit, Mail, Calendar, Shield, Settings } from "lucide-react";

const formSchema = z.object({
  firstName: z.string().min(1, "First name is required"),
  lastName: z.string().min(1, "Last name is required"),
  email: z.string().email("Invalid email address"),
  bio: z.string().max(500, "Bio must be less than 500 characters"),
  website: z.string().url("Invalid URL").optional(),
});

type FormValues = z.infer<typeof formSchema>;

export default function Profile() {
  const { register, handleSubmit, formState: { errors } } = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      firstName: "John",
      lastName: "Doe",
      email: "john.doe@example.com",
      bio: "AI enthusiast and developer",
      website: "https://example.com",
    },
  });

  const [isSaving, setIsSaving] = useState(false);

  const handleSubmitForm = async (data: FormValues) => {
    setIsSaving(true);
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setIsSaving(false);
    // In a real app, we would show a success message
    alert("Profile updated successfully!");
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
          <div className="flex-1 lg:w-1/2">
            <h1 className="text-2xl font-bold text-foreground mb-4">Profile</h1>
            <p className="text-muted-foreground">
              Manage your account information and preferences
            </p>
          </div>

          <div className="flex-1 lg:w-1/2 lg:mt-0 lg:flex lg:items-end lg:justify-end space-x-4">
            <Button
              variant="outline"
              onClick={() => {
                // In a real app, we would open a modal or navigate to edit mode
                alert("Edit profile functionality would go here");
              }}
            >
              Edit Profile
            </Button>
            <Button
              variant="default"
              onClick={handleSubmit(handleSubmitForm)}
              disabled={isSaving}
              className="w-full lg:w-auto"
            >
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>

        <div className="grid gap-6">
          <div className="col-span-2 lg:col-span-1">
            <Card className="h-full">
              <CardHeader>
                <h2 className="text-lg font-semibold text-foreground">
                  Personal Information
                </h2>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground block">
                      First Name
                    </label>
                    <input
                      {...register("firstName")}
                      placeholder="Enter your first name"
                      className={cn(
                        "block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                        errors.firstName && "border-destructive"
                      )}
                    />
                    {errors.firstName && (
                      <p className="text-xs text-destructive mt-1">
                        {errors.firstName.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground block">
                      Last Name
                    </label>
                    <input
                      {...register("lastName")}
                      placeholder="Enter your last name"
                      className={cn(
                        "block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                        errors.lastName && "border-destructive"
                      )}
                    />
                    {errors.lastName && (
                      <p className="text-xs text-destructive mt-1">
                        {errors.lastName.message}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium text-muted-foreground block">
                      Email
                    </label>
                    <input
                      type="email"
                      {...register("email")}
                      placeholder="Enter your email address"
                      className={cn(
                        "block w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
                        errors.email && "border-destructive"
                      )}
                    />
                    {errors.email && (
                      <p className="text-xs text-destructive mt-1">
                        {errors.email.message}
                      </p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="col-span-2 lg:col-span-1">
            <Card className="h-full">
              <CardHeader>
                <h2 className="text-lg font-semibold text-foreground">
                  Biography
                </h2>
              </CardHeader>
              <CardContent>
                <textarea
                  {...register("bio")}
                  placeholder="Tell us about yourself..."
                  className="block w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                />
                {errors.bio && (
                  <p className="text-xs text-destructive mt-1">
                    {errors.bio.message}
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <div className="col-span-2 lg:col-span-1">
            <Card className="h-full">
              <CardHeader>
                <h2 className="text-lg font-semibold text-foreground">
                  Account Settings
                </h2>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <Shield className="h-5 w-5 text-primary" />
                    <div>
                      <h3 className="font-medium text-foreground">Security</h3>
                      <p className="text-sm text-muted-foreground">
                        Manage your account security settings
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Settings className="h-5 w-5 text-primary" />
                    <div>
                      <h3 className="font-medium text-foreground">Preferences</h3>
                      <p className="text-sm text-muted-foreground">
                        Customize your experience
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Mail className="h-5 w-5 text-primary" />
                    <div>
                      <h3 className="font-medium text-foreground">Notifications</h3>
                      <p className="text-sm text-muted-foreground">
                        Control email and in-app notifications
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
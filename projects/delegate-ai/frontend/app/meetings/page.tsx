import { MainLayout } from "@/components/layout/main-layout"
import { MeetingManagement } from "@/components/meetings/meeting-management"

export default function MeetingsPage() {
  return (
    <MainLayout>
      <MeetingManagement />
    </MainLayout>
  )
}
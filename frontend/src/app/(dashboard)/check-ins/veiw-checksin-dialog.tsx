import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogFooter,
} from "@/components/ui/dialog";

type CheckInRow = {
    id: number;
    name: string;
    date: string;
    mood: string;
    score: string;
};

export default function ViewCheckInDialog({
    checkIn,
    open,
    onOpenChange,
}: {
    checkIn: CheckInRow | null;
    open: boolean;
    onOpenChange: (v: boolean) => void;
}) {
    if (!checkIn) return null;

    return (
        <Dialog open={open} onOpenChange={onOpenChange}>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Check-In Details</DialogTitle>
                </DialogHeader>

                <div className="space-y-2">
                    <p>
                        <strong>Name:</strong> {checkIn.name}
                    </p>
                    <p>
                        <strong>Date:</strong> {checkIn.date}
                    </p>
                    <p>
                        <strong>Mood:</strong> {checkIn.mood}
                    </p>
                    <p>
                        <strong>Score:</strong> {checkIn.score}
                    </p>
                </div>

                <DialogFooter>
                    <Button variant="outline" onClick={() => onOpenChange(false)}>
                        Close
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
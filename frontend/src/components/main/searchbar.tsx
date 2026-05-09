import { Funnel, Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export function SearchBar() {
    return (
        <div className="w-full max-w-screen-2xl mx-auto px-4 sm:px-6 lg:px-8 xl:px-12 py-0">
            <div className="flex flex-wrap gap-3 sm:gap-4 md:gap-5 items-center justify-between md:flex-col md:items-start lg:flex-row lg:items-center lg:justify-between">
                {/* Main Search */}
                <div className="flex flex-wrap gap-3 sm:gap-4 md:gap-5 flex-1 w-full min-w-0 md:w-auto">
                    <div className="relative w-full md:w-auto md:flex-1 md:max-w-xs lg:max-w-sm">
                        <Input
                            type="text"
                            placeholder="Enter keywords"
                            className="h-auto w-full rounded-[20px] border border-border bg-background px-4 sm:px-5 py-3 sm:py-4 pr-12 text-base sm:text-lg md:text-lg text-muted-foreground placeholder:text-muted-foreground"
                        />
                        <Search className="absolute right-4 sm:right-5 top-1/2 -translate-y-1/2 size-5 sm:size-6 md:size-7 text-muted-foreground" />
                    </div>
                    <Button className="h-auto w-full sm:w-auto rounded-[20px] border border-border bg-background px-3 sm:px-4 md:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground hover:bg-muted">
                        #ID
                    </Button>
                </div>

                {/* Advanced Search & Filters */}
                <div className="flex flex-wrap gap-3 sm:gap-4 md:gap-5 w-full md:w-auto flex-1 md:flex-initial">
                    <Button className="h-auto flex-1 md:flex-initial md:w-auto rounded-[20px] border border-border bg-background px-3 sm:px-4 md:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground hover:bg-muted">
                        Advance Search
                    </Button>
                    <Button className="flex h-auto flex-1 md:flex-initial md:w-auto items-center gap-2 rounded-[20px] border border-border bg-background px-3 sm:px-4 md:px-9 py-3 sm:py-4 text-sm sm:text-base md:text-lg font-normal leading-normal text-muted-foreground hover:bg-muted">
                        Filters
                        <Funnel className="size-5 sm:size-6 md:size-7" />
                    </Button>
                </div>
            </div>
        </div>
    );
}

import React from 'react';
import { Roadmap as RoadmapComponent } from '@/components/Roadmap'; // Import the component we want to reuse

// This page will display the full roadmap without pagination
// We can potentially reuse the Roadmap component structure or create a dedicated one.
// For simplicity, let's reuse the existing component logic structure but render all items.
// NOTE: This assumes the Roadmap component can be adapted or we extract its core rendering logic.
// A cleaner approach might be to create a dedicated FullRoadmap component.

// Let's adjust this later if needed. For now, just render the title.
// Re-importing parts of the Roadmap component logic directly for now.

import { ArrowDownNarrowWide, Clock, CheckCircle, AlertCircle, PauseCircle, Github } from 'lucide-react';
import { Task, roadmapTasks } from '@/data/roadmapData'; // Import data
import styles from '@/components/Roadmap.module.css'; // Reuse styles
import { Button } from '@/components/ui/button';
import Link from 'next/link';

// Helper function to get status icon (copied from Roadmap.tsx)
const getStatusIcon = (status: Task['status']) => {
    switch (status) {
        case 'DONE': return <CheckCircle className="h-4 w-4 text-green-500" />;
        case 'In Progress': return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
        case 'Planned': return <AlertCircle className="h-4 w-4 text-yellow-500" />;
        // Removed cases for 'Paused', 'Blocked', 'Completed' as they are not in the Task type
        // case 'Paused': return <PauseCircle className="h-4 w-4 text-gray-500" />;
        default: return <AlertCircle className="h-4 w-4 text-gray-500" />; // Default case for safety
    }
};

// Helper function to get priority badge (copied from Roadmap.tsx)
const getPriorityBadge = (priority: Task['priority']) => {
    switch(priority) {
        case 'CRITICAL': return <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Critical</span>;
        case 'HIGH': return <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">High</span>;
        case 'MEDIUM': return <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Medium</span>;
        case 'LOW': return <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Low</span>;
        default: return <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">Unknown</span>;
    }
};


export default function FullRoadmapPage() {
    // We won't implement the modal click here for simplicity, focusing on display
    // A better implementation would abstract the table into its own component.
    return (
        <div className="container mx-auto px-4 py-12">
            <Link href="/" passHref>
                 <Button variant="outline" className="mb-6">&larr; Voltar para Home</Button>
            </Link>
            <h1 className="text-3xl font-bold text-center mb-8">EGOS Project Roadmap (Completo)</h1>
            
            <div className="overflow-x-auto rounded-lg shadow">
                <table className="min-w-full divide-y divide-border">
                    <thead className="bg-muted/50">
                        <tr className="border-b transition-colors">
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Subsystem(s)</th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Task ID</th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Priority</th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Description</th>
                            <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Details/Link</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border bg-card">
                        {roadmapTasks.map((item, index) => (
                            <tr key={index} className="hover:bg-muted/50 transition-colors">
                                <td className="p-4 align-middle whitespace-nowrap">{getStatusIcon(item.status)} {item.status}</td>
                                <td className="p-4 align-middle whitespace-nowrap">{item.subsystem}</td>
                                <td className="p-4 align-middle font-mono text-sm whitespace-nowrap">{item.id}</td>
                                <td className="p-4 align-middle whitespace-nowrap">{getPriorityBadge(item.priority)}</td>
                                <td className="p-4 align-middle text-sm min-w-[300px]">{item.title}</td>
                                <td className="p-4 align-middle text-xs">
                                    {/* Link to GitHub issue based on ID */}
                                    <a 
                                        href={`https://github.com/enioxt/egos/issues?q=is%3Aissue+is%3Aopen+label%3A${item.id}`}
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
                                    >
                                        <Github className="mr-1 h-3 w-3" /> GitHub
                                    </a>
                                    {/* Optionally show details on hover/click later */}
                                    {/* <p className="mt-1 text-muted-foreground truncate max-w-xs">{item.details}</p> */}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowDownNarrowWide, Clock, CheckCircle, AlertCircle, PauseCircle, X, ExternalLink, Github, PlusCircle, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Task, roadmapTasks } from '../data/roadmapData';

// Helper function to get status icon
const getStatusIcon = (status: string) => {
  switch(status) {
    case 'Done':
      return <CheckCircle className="h-5 w-5 text-green-500" />;
    case 'In Progress':
      return <Clock className="h-5 w-5 text-blue-500" />;
    case 'Blocked':
      return <PauseCircle className="h-5 w-5 text-red-500" />;
    case 'To Do':
      return <AlertCircle className="h-5 w-5 text-amber-500" />;
    default:
      return null;
  }
};

// Helper function to get priority badge
const getPriorityBadge = (priority: string) => {
  switch(priority) {
    case 'Critical':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">Critical</span>;
    case 'High':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200">High</span>;
    case 'Medium':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Medium</span>;
    case 'Low':
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Low</span>;
    default:
      return <span className="px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">Unknown</span>;
  }
};

export const Roadmap = () => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showContribution, setShowContribution] = useState(false);
  const [visibleCount, setVisibleCount] = useState(5);

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setShowContribution(true);
  };

  const handleCloseModal = () => {
    setShowContribution(false);
  };

  const handleShowMore = () => {
    setVisibleCount(prevCount => Math.min(prevCount + 5, roadmapTasks.length));
  };

  return (
    <section id="roadmap" className="py-16 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">Roadmap do Projeto</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Acompanhe o progresso do desenvolvimento do EGOS e as próximas etapas planejadas.
          </p>
        </div>
        
        <div className="overflow-x-auto rounded-lg shadow">
          <table className="min-w-full divide-y divide-border">
            <thead className="bg-muted/50">
              <tr className="border-b transition-colors hover:bg-muted/50">
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Status</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Subsystem(s)</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Task ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Priority</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Description</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-card">
              {roadmapTasks.slice(0, visibleCount).map((item, index) => (
                <tr 
                  key={index} 
                  className="hover:bg-muted/50 transition-colors cursor-pointer" 
                  onClick={() => handleTaskClick(item)}
                >
                  <td className="p-4 align-middle">{getStatusIcon(item.status)} {item.status}</td>
                  <td className="p-4 align-middle">{item.subsystem}</td>
                  <td className="p-4 align-middle font-mono text-sm">{item.id}</td>
                  <td className="p-4 align-middle">{getPriorityBadge(item.priority)}</td>
                  <td className="p-4 align-middle text-sm">{item.title}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Show More / View Full Buttons */}
        <div className="mt-6 flex flex-col sm:flex-row justify-center items-center gap-4">
          {visibleCount < roadmapTasks.length && (
            <Button variant="outline" onClick={handleShowMore}>
              <PlusCircle className="mr-2 h-4 w-4" />
              Ver Mais ({roadmapTasks.length - visibleCount} restantes)
            </Button>
          )}
          <Link href="/roadmap" passHref>
            <Button variant="secondary">
               Ver Roadmap Completo
               <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>

        {/* Contribution Modal */}
        {showContribution && selectedTask && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
            <div className="relative w-full max-w-2xl rounded-lg bg-card p-6 shadow-lg">
              <Button 
                variant="ghost" 
                size="icon" 
                className="absolute right-4 top-4 rounded-full" 
                onClick={handleCloseModal}
              >
                <X className="h-4 w-4" />
              </Button>
              <h3 className="text-lg font-semibold mb-4">Task Details: {selectedTask.id}</h3>
              <p className="mb-2"><strong className="text-muted-foreground">Title:</strong> {selectedTask.title}</p>
              <p className="mb-2"><strong className="text-muted-foreground">Status:</strong> {getStatusIcon(selectedTask.status)} {selectedTask.status}</p>
              <p className="mb-2"><strong className="text-muted-foreground">Priority:</strong> {getPriorityBadge(selectedTask.priority)}</p>
              <p className="mb-2"><strong className="text-muted-foreground">Subsystem:</strong> {selectedTask.subsystem}</p>
              <p className="mb-4 whitespace-pre-wrap"><strong className="text-muted-foreground">Details:</strong> {selectedTask.details}</p>
              
              {/* Placeholder for LLM Integration & Contribution Guide */}
              <div className="mt-4 rounded border p-4 bg-muted/30">
                <h4 className="font-medium mb-2">Contribution Guide & AI Assistant</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Ready to contribute? Click the link below to view the relevant files on GitHub. 
                  Use the AI assistant (coming soon!) for guidance on implementation, understanding dependencies, 
                  or adhering to project principles.
                </p>
                {/* Example GitHub link - Needs to be dynamic based on task context */}
                <Button variant="outline" size="sm" asChild>
                  <a href={`https://github.com/enioxt/egos/issues?q=is%3Aissue+is%3Aopen+label%3A${selectedTask.id}`} target="_blank" rel="noopener noreferrer">
                    <Github className="mr-2 h-4 w-4" /> View/Discuss on GitHub
                  </a>
                </Button>
                 {/* Placeholder for AI Chat Interface */}
                 <div className="mt-3 text-center text-xs text-muted-foreground">[AI Assistant Interface Placeholder]</div>
              </div>

              {/* Optional: Add direct link to related docs or code if parseable from details */}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

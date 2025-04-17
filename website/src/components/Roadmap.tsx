'use client';

import React, { useState, useEffect, useCallback, useRef } from 'react';
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

// Helper function to group and sort tasks
const groupAndSortTasks = (tasks: Task[]) => {
  const inProgress = tasks.filter(t => t.status === 'In Progress').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  const planned = tasks.filter(t => t.status === 'Planned').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  const completed = tasks.filter(t => t.status === 'Completed' || t.status === 'DONE').sort((a, b) => priorityOrder(a.priority) - priorityOrder(b.priority));
  return { inProgress, planned, completed };
};

const priorityOrder = (priority: string) => {
  switch(priority) {
    case 'CRITICAL': return 1;
    case 'HIGH': return 2;
    case 'MEDIUM': return 3;
    case 'LOW': return 4;
    default: return 5;
  }
};

export const Roadmap = () => {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showContribution, setShowContribution] = useState(false);
  const [visibleCount, setVisibleCount] = useState(5);
  const modalRef = useRef<HTMLDivElement>(null);

  const { inProgress, planned, completed } = groupAndSortTasks(roadmapTasks);
  const allTasks = [...inProgress, ...planned, ...completed];

  // Define priority order
  const priorityOrder: { [key: string]: number } = {
    'Critical': 1,
    'High': 2,
    'Medium': 3,
    'Low': 4,
    'Unknown': 5, // Treat Unknown like Low or last
  };

  // Define status order
  const statusOrder: { [key: string]: number } = {
    'In Progress': 1,
    'Blocked': 2,
    'To Do': 3, // Assuming 'To Do' exists or is similar to Planned
    'Planned': 3, // Group Planned and To Do
    'Done': 4,
  };

  // Sort tasks
  const sortedTasks = [...roadmapTasks].sort((a, b) => {
    const statusDiff = (statusOrder[a.status] ?? 99) - (statusOrder[b.status] ?? 99);
    if (statusDiff !== 0) {
      return statusDiff;
    }
    // If statuses are the same, sort by priority
    const priorityDiff = (priorityOrder[a.priority] ?? 99) - (priorityOrder[b.priority] ?? 99);
    return priorityDiff;
  });

  const totalTasks = sortedTasks.length;

  const handleTaskClick = (task: Task) => {
    setSelectedTask(task);
    setShowContribution(true);
  };

  const handleCloseModal = () => {
    setShowContribution(false);
  };

  const handleShowMore = () => {
feat/roadmap-updates
    setVisibleCount(prevCount => Math.min(prevCount + 5, totalTasks));

    setVisibleCount(prevCount => Math.min(prevCount + 5, allTasks.length));
main
  };

  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (event.key === 'Escape') {
      handleCloseModal();
    }
  }, []);

  const handleClickOutside = useCallback((event: MouseEvent) => {
    if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
      const backdrop = document.querySelector('.fixed.inset-0.z-50');
      if (event.target === backdrop) {
        handleCloseModal();
      }
    }
  }, []);

  useEffect(() => {
    if (showContribution) {
      document.addEventListener('keydown', handleKeyDown);
      document.addEventListener('mousedown', handleClickOutside);
    } else {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showContribution, handleKeyDown, handleClickOutside]);

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
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Subsistema(s)</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">ID</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Prioridade</th>
                <th className="h-12 px-4 text-left align-middle font-medium text-muted-foreground">Descrição</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-card">
feat/roadmap-updates
              {sortedTasks.slice(0, visibleCount).map((item, index) => (

              {allTasks.slice(0, visibleCount).map((item, index) => (
main
                <tr 
                  key={index} 
                  className={`hover:bg-muted/50 transition-colors cursor-pointer ${item.status === 'Completed' || item.status === 'DONE' ? 'opacity-60' : ''}`} 
                  onClick={() => handleTaskClick(item)}
                >
                  <td className="p-4 align-middle">{getStatusIcon(item.status)} {item.status === 'DONE' ? 'Completed' : item.status}</td>
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
feat/roadmap-updates
          {visibleCount < totalTasks && (
            <Button variant="outline" onClick={handleShowMore}>
              <PlusCircle className="mr-2 h-4 w-4" />
              Ver Mais ({totalTasks - visibleCount} restantes)

          {visibleCount < allTasks.length && (
            <Button variant="outline" onClick={handleShowMore}>
              <PlusCircle className="mr-2 h-4 w-4" />
              Ver Mais ({allTasks.length - visibleCount} restantes)
main
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
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm">
            <div ref={modalRef} className="relative w-full max-w-xl rounded-2xl bg-neutral-900 bg-gradient-to-br from-neutral-900 via-neutral-800 to-neutral-900 border border-border shadow-2xl p-8 mx-2 animate-fade-in">
              <Button 
                variant="ghost" 
                size="icon" 
                className="absolute right-4 top-4 rounded-full text-muted-foreground hover:text-foreground" 
                onClick={handleCloseModal}
              >
                <X className="h-5 w-5" />
              </Button>
              <h3 className="text-xl font-bold mb-4 text-foreground">Detalhes da Tarefa: <span className="font-mono text-base text-blue-300">{selectedTask.id}</span></h3>
              <div className="mb-3 flex flex-wrap gap-4 items-center text-sm">
                <span className="font-medium text-muted-foreground">Status:</span> {getStatusIcon(selectedTask.status)} <span className="text-blue-400">{selectedTask.status === 'DONE' ? 'Completed' : selectedTask.status}</span>
                <span className="font-medium text-muted-foreground">Prioridade:</span> {getPriorityBadge(selectedTask.priority)}
                {selectedTask.phase && <><span className="font-medium text-muted-foreground">Fase:</span> <span className="text-purple-300">{selectedTask.phase}</span></>}
              </div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Subsistema(s):</span> <span className="text-foreground">{selectedTask.subsystem || '-'}</span></div>
              <div className="mb-2 text-lg font-semibold text-foreground"><span className="">Título:</span> {selectedTask.title}</div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Descrição:</span> <span className="text-foreground">{selectedTask.description || '-'}</span></div>
              <div className="mb-2 whitespace-pre-wrap text-sm"><span className="font-medium text-muted-foreground">Detalhes:</span> <span className="text-foreground">{selectedTask.details}</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Dependências:</span> <span className="italic text-muted-foreground">(Preencher se houver)</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Princípios Relacionados:</span> <span className="italic text-muted-foreground">(Preencher se houver)</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Stack Recomendada:</span> <span className="italic text-muted-foreground">(Ex: Next.js, Tailwind, Node.js, Pinecone, OpenAI API)</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Tempo Estimado (IA):</span> <span className="italic text-muted-foreground">(Ex: 1-2h)</span> <span className="ml-4 font-medium text-muted-foreground">Tempo Estimado (Humano):</span> <span className="italic text-muted-foreground">(Ex: 2-4h)</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Rastreamento de Tempo:</span> <span className="italic text-muted-foreground">(Preencher quando disponível)</span></div>
              <div className="mb-2 text-sm"><span className="font-medium text-muted-foreground">Recompensa / ETHIK:</span> <span className="italic text-muted-foreground">(Ex: 10 ETHIK tokens)</span></div>
              <div className="my-4 rounded-xl border border-border p-4 bg-neutral-800 bg-gradient-to-br from-neutral-800 via-neutral-900 to-neutral-800">
                <h4 className="font-semibold mb-2 text-blue-200 flex items-center gap-2"><PanelRight className="h-5 w-5" /> Como Contribuir</h4>
                <ol className="list-decimal ml-5 text-sm mb-3 text-foreground">
                  <li>
                    Leia o <a href="/roadmap" className="underline text-blue-400 hover:text-blue-200" target="_blank">roadmap completo</a> para entender o contexto e as prioridades.
                  </li>
                  <li>
                    Leia as <a href={selectedTask.link || 'https://github.com/enioxt/egos#roadmap'} className="underline text-blue-400 hover:text-blue-200" target="_blank">instruções completas e critérios de aceitação</a> no GitHub.
                  </li>
                  <li>
                    Siga as <a href="https://github.com/enioxt/egos/blob/main/CONTRIBUTING.md" className="underline text-blue-400 hover:text-blue-200" target="_blank">regras do sistema EGOS</a> (contribuição, padrões, ética).
                  </li>
                </ol>
                <div className="mb-2 flex items-center gap-2 text-sm">
                  <span className="font-medium text-muted-foreground">Critérios de Aceitação:</span>
                  <span className="italic text-muted-foreground">(Descreva claramente o que define a tarefa como concluída, conforme o roadmap e GitHub)</span>
                </div>
                <div className="mb-2 flex items-center gap-2 text-sm">
                  <span className="font-medium text-muted-foreground">Regras EGOS:</span>
                  <span className="italic text-muted-foreground">(Padrões, ética, acessibilidade, documentação, segurança, etc.)</span>
                </div>
                {selectedTask.link ? (
                  <Button variant="outline" size="sm" asChild className="mt-2">
                    <a href={selectedTask.link} target="_blank" rel="noopener noreferrer">
                      <Github className="mr-2 h-4 w-4" /> Ver Código ou Discussão no GitHub
                    </a>
                  </Button>
                ) : (
                  <Button variant="outline" size="sm" asChild className="mt-2">
                    <a href="/roadmap" target="_blank" rel="noopener noreferrer">
                      <ArrowRight className="mr-2 h-4 w-4" /> Ver Roadmap Completo
                    </a>
                  </Button>
                )}
                <div className="mt-3 text-center text-xs text-muted-foreground">[AI Assistant Interface Placeholder]</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

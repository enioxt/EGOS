'use client';

import React, { useState } from 'react';
import { ArrowDownNarrowWide, Clock, CheckCircle, AlertCircle, PauseCircle, X, ExternalLink, Github } from 'lucide-react';
import { Button } from '@/components/ui/button';

// Dados do roadmap baseados no ROADMAP.md
const roadmapItems = [
  {
    status: 'Done',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-001',
    priority: 'Critical',
    description: 'Migrate core landing page components (Header, Hero, Principles, Subsystems, CTA, Footer) from `lovable` project.',
    dependencies: '-',
    principles: 'Modularity, Preservation'
  },
  {
    status: 'Done',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-002',
    priority: 'High',
    description: 'Set up Shadcn/UI and Tailwind CSS configuration.',
    dependencies: '-',
    principles: 'Modularity'
  },
  {
    status: 'Done',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-003',
    priority: 'High',
    description: 'Integrate migrated components into the main landing page (`src/app/page.tsx`).',
    dependencies: 'WEB-001',
    principles: 'Modularity'
  },
  {
    status: 'Done',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-005',
    priority: 'High',
    description: 'Fix SVG components and animations for visual elements.',
    dependencies: 'WEB-002',
    principles: 'Universal Accessibility'
  },
  {
    status: 'Done',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-004',
    priority: 'Medium',
    description: 'Test and verify the appearance and functionality of the landing page components.',
    dependencies: 'WEB-003',
    principles: 'Integrated Ethics'
  },
  {
    status: 'To Do',
    subsystems: 'Frontend, I18n',
    taskId: 'WEB-006',
    priority: 'Low',
    description: 'Implementar suporte a internacionalização (i18n) para português e inglês.',
    dependencies: 'WEB-004',
    principles: 'Universal Accessibility'
  },
  {
    status: 'To Do',
    subsystems: 'Frontend, UI/UX',
    taskId: 'WEB-007',
    priority: 'Medium',
    description: 'Otimizar responsividade para dispositivos móveis.',
    dependencies: 'WEB-004',
    principles: 'Universal Accessibility'
  },
  {
    status: 'To Do',
    subsystems: 'Frontend, Content',
    taskId: 'WEB-008',
    priority: 'Medium',
    description: 'Adicionar seção de Blog/Notícias com últimas atualizações do projeto.',
    dependencies: 'WEB-004',
    principles: 'Modularity, Systemic Cartography'
  }
];

// Função de renderização do ícone de status
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

// Função para determinar a cor de fundo baseada na prioridade
const getPriorityClass = (priority: string) => {
  switch(priority) {
    case 'Critical':
      return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
    case 'High':
      return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200';
    case 'Medium':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
    case 'Low':
      return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
  }
};

export const Roadmap = () => {
  const [selectedTask, setSelectedTask] = useState<(typeof roadmapItems)[0] | null>(null);
  const [showContribution, setShowContribution] = useState(false);
  
  const handleTaskClick = (task: typeof roadmapItems[0]) => {
    setSelectedTask(task);
    setShowContribution(true);
  };

  const closeContributionModal = () => {
    setShowContribution(false);
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
            <thead className="bg-muted">
              <tr>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    Status
                  </div>
                </th>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  <div className="flex items-center gap-1">
                    Task ID
                    <ArrowDownNarrowWide className="h-4 w-4" />
                  </div>
                </th>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground">
                  Descrição
                </th>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Prioridade
                </th>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Subsistemas
                </th>
                <th scope="col" className="px-4 py-3.5 text-left text-sm font-semibold text-foreground whitespace-nowrap">
                  Princípios
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border bg-card">
              {roadmapItems.map((item, index) => (
                <tr 
                  key={index} 
                  className="hover:bg-muted/50 transition-colors cursor-pointer" 
                  onClick={() => handleTaskClick(item)}
                >
                  <td className="px-4 py-4 text-sm whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {getStatusIcon(item.status)}
                      <span>{item.status}</span>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm font-medium whitespace-nowrap">
                    {item.taskId}
                  </td>
                  <td className="px-4 py-4 text-sm">
                    <div className="max-w-xs md:max-w-lg">
                      {item.description}
                      {item.dependencies !== '-' && (
                        <div className="mt-1 text-xs text-muted-foreground">
                          Deps: {item.dependencies}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="px-4 py-4 text-sm whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityClass(item.priority)}`}>
                      {item.priority}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-sm whitespace-nowrap">
                    {item.subsystems}
                  </td>
                  <td className="px-4 py-4 text-sm whitespace-nowrap">
                    {item.principles}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        
        {/* Contribution Modal */}
        {showContribution && selectedTask && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-card rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-auto">
              <div className="p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-bold text-foreground">{selectedTask.taskId}: {selectedTask.description}</h3>
                  <button 
                    onClick={closeContributionModal}
                    className="text-muted-foreground hover:text-foreground"
                  >
                    <X className="h-5 w-5" />
                  </button>
                </div>
                
                <div className="mb-6">
                  <div className="flex items-center gap-2 mb-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityClass(selectedTask.priority)}`}>
                      {selectedTask.priority}
                    </span>
                    <span className="text-sm text-muted-foreground">{selectedTask.subsystems}</span>
                  </div>
                  <p className="text-muted-foreground text-sm mb-4">This task aligns with the EGOS principles of {selectedTask.principles}.</p>
                  
                  <div className="bg-muted p-4 rounded-md mb-4">
                    <h4 className="font-medium mb-2">How to Contribute</h4>
                    <p className="text-sm mb-3">You can contribute to this task in several ways:</p>
                    <ul className="text-sm space-y-2">
                      <li className="flex items-start gap-2">
                        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-primary text-xs">1</span>
                        </div>
                        <span>Fork the <a href="https://github.com/enioxt/EGOS" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">EGOS repository</a> on GitHub</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-primary text-xs">2</span>
                        </div>
                        <span>Create a new branch with a descriptive name related to this task</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-primary text-xs">3</span>
                        </div>
                        <span>Implement your solution following our <a href="https://github.com/enioxt/EGOS/blob/main/CONTRIBUTING.md" target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">contribution guidelines</a></span>
                      </li>
                      <li className="flex items-start gap-2">
                        <div className="w-5 h-5 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                          <span className="text-primary text-xs">4</span>
                        </div>
                        <span>Submit a pull request and earn ETHIK tokens upon approval</span>
                      </li>
                    </ul>
                  </div>
                  
                  <div className="space-y-4">
                    <h4 className="font-medium">Get Help from Our AI Assistant</h4>
                    <p className="text-sm text-muted-foreground">Our EGOS AI assistant can provide guidance specific to this task, helping you understand the requirements and implementation details.</p>
                    <div className="flex gap-3 flex-wrap">
                      <a href="https://github.com/enioxt/EGOS/discussions" target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="gap-2">
                          <Github className="h-4 w-4" />
                          Join Discussion
                        </Button>
                      </a>
                      <a href="https://t.me/EGOSproject" target="_blank" rel="noopener noreferrer">
                        <Button variant="outline" size="sm" className="gap-2">
                          <ExternalLink className="h-4 w-4" />
                          Telegram Community
                        </Button>
                      </a>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end mt-4">
                  <Button onClick={closeContributionModal}>
                    Close
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
};

const groups = {
  canopy: [
    ['Retained wall', 'Older masonry and concrete remain visible beneath the added canopy.'],
    ['Replaceable glass', 'Separate optical cassettes include an open replacement position.'],
    ['Attachment + service rib', 'Mechanical attachment and a service route occupy their own part of the roof.'],
    ['Data + electrical services', 'Blue dashed optical/data and amber dash-dot electrical paths remain distinct interfaces.'],
    ['Passage + maintenance', 'Public passage and maintenance need separate clearance and conditional access.'],
    ['Property break', 'The canopy stops before an unconnected neighboring structure; agreement is not assumed.'],
  ],
  farm: [
    ['Open field', 'Productive cultivation remains substantially unroofed.'],
    ['Selective propagation', 'A translucent cultivation bay occupies only one segment of the working edge.'],
    ['Machine repair', 'A stopped field machine and unavailable seam segment make service and interruption visible.'],
    ['Contained work + hold', 'Opaque processing and qualification remain separate from cultivation, with held/rejected material and an outward route.'],
    ['Drainage + wetland', 'An older gate, ordinary ditch water and distinct reed wetland remain separate spaces. Clearing sediment shows work, without demonstrating treatment.'],
    ['Outside supply', 'Conventional receiving, service and outward access keep external dependencies visible.'],
  ],
  industry: [
    ['Retained hall', 'Older masonry and crane structure frame the proposed exchange frontage.'],
    ['Cell + empty berth', 'A removable opaque cell and isolated berth make replacement and interruption visible.'],
    ['Staffed qualification', 'A protected optical gallery and human desk occupy a distinct workspace.'],
    ['Accessible services', 'Heat and water interfaces include service access and outside dependencies.'],
    ['Separate material bays', 'Left to right: incoming, held/rejected, conditionally qualified and outgoing residual material. Qualification does not guarantee use.'],
    ['Outside freight', 'Supplies and residual handling cross the hall’s boundary.'],
  ],
} as const;

export function insetCallouts(key: keyof typeof groups): string {
  return `<ol class="inset-callouts" aria-label="Six numbered areas in the section">${groups[key].map(([title, text], i) => `<li><strong>${String(i + 1).padStart(2, '0')} / ${title}</strong><span>${text}</span></li>`).join('')}</ol>`;
}

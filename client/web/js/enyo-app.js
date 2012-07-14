/* App.js */

enyo.kind({
    name: "App",
    classes: "enyo-unselectable",
    components: [

        { name: "snapscroller", kind: "SnapScroller", classes: "scroller",
            horizontal: "scroll", vertical: "hidden", // only scroll horizontal
            // css required to stack items horizontally for scroll
            components: [
                {kind: "List", name: "list1", classes: "list scroller-slide", fit: false, multiSelect: true, onSetupItem: "setupItem", components: [
                        {name: "divider1", classes: "divider"},
                        {name: "item1", kind: "ContactItem", classes: "item enyo-border-box", onRemove: "removeTap"}
                ]},
                {kind: "List", name: "list2", classes: "list scroller-slide", fit: false, multiSelect: true, onSetupItem: "setupItem", components: [
                        {name: "divider2", classes: "divider"},
                        {name: "item2", kind: "ContactItem", classes: "item enyo-border-box", onRemove: "removeTap"}
                ]},
                {kind: "List", name: "list3", classes: "list scroller-slide", fit: false, multiSelect: true, onSetupItem: "setupItem", components: [
                    {name: "divider3", classes: "divider"},
                    {name: "item3", kind: "ContactItem", classes: "item enyo-border-box", onRemove: "removeTap"}
                ]}
            ]
        }
    ],
    rendered: function() {
        this.inherited(arguments);
        this.populateList();
    },
    populateList: function() {
        this.$.list1.setCount(100);
        this.$.list1.reset();
        this.$.list2.setCount(100);
        this.$.list2.reset();
        this.$.list3.setCount(100);
        this.$.list3.reset();
    },
    setupItem: function(inSender, inEvent) {
        var i = inEvent.index;
        console.log(i);
        (this.$.item1 || this.$.item2 || this.$.item3).setContact({
            name: "Conact " + i,
            title: "Something goes here",
            avatar: ""
       });
    }
});

// It's convenient to create a kind for the item we'll render in the contacts list.
enyo.kind({
    name: "ContactItem",
        events: {
        onRemove: ""
    },
    components: [
        {name: "avatar", kind: "Image", classes: "avatar"},
        {components: [
            {name: "name"},
            {name: "title", classes: "description"},
            {content: "(415) 711-1234", classes: "description"}
        ]}
    ],
    setContact: function(inContact) {
        this.$.name.setContent(inContact.name);
        this.$.avatar.setSrc(inContact.avatar);
        this.$.title.setContent(inContact.title);
    },
    setSelected: function(inSelected) {
        this.addRemoveClass("item-selected", inSelected);
        this.$.remove.applyStyle("display", inSelected ? "inline-block" : "none");
    },
    removeTap: function(inSender, inEvent) {
        this.doRemove(inEvent);
        return true;
    }
});